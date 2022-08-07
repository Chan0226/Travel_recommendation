from django.shortcuts import render, redirect
from django.db import transaction
from django.core.paginator import Paginator

from django.core.serializers.json import DjangoJSONEncoder
import json
from django.http import HttpResponse, request, response

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
import sklearn as sk
import warnings
# 직렬화
from rest_framework import viewsets
import csv
import random

from .models import *

from django.conf import settings
from user.models import User

warnings.filterwarnings('ignore')


# 우리가 예측한 평점과 실제 평점간의 차이를 MSE로 계산
def get_mse(pred, actual):
    # 평점이 있는 실제 영화만 추출
    pred = pred[actual.nonzero()].flatten()
    actual = actual[actual.nonzero()].flatten()
    return mean_squared_error(pred, actual)


# 특정 도시와 비슷한 유사도를 가지는 도시 Top_N에 대해서만 적용 -> 시간오래걸림
def predict_rating_topsim(ratings_arr, item_sim_arr, n=20):
    # 사용자-아이템 평점 행렬 크기만큼 0으로 채운 예측 행렬 초기화
    pred = np.zeros(ratings_arr.shape)

    # 사용자-아이템 평점 행렬의 도시 개수만큼 루프
    for col in range(ratings_arr.shape[1]):
        # 유사도 행렬에서 유사도가 큰 순으로 n개의 데이터 행렬의 인덱스 반환
        top_n_items = [np.argsort(item_sim_arr[:, col])[:-n - 1:-1]]
        # 개인화된 예측 평점 계산 : 각 col 도시별(1개), 2496 사용자들의 예측평점
        for row in range(ratings_arr.shape[0]):
            pred[row, col] = item_sim_arr[col, :][top_n_items].dot(
                ratings_arr[row, :][top_n_items].T)
            pred[row, col] /= np.sum(item_sim_arr[col, :][top_n_items])

    return pred


def get_not_tried_beer(ratings_matrix, userId):
    # userId로 입력받은 사용자의 모든 도시 정보를 추출해 Series로 반환
    # 반환된 user_rating은 영화명(title)을 인덱스로 가지는 Series 객체
    user_rating = ratings_matrix.loc[userId, :]

    # user_rating이 0보다 크면 기존에 관란함 영화.
    # 대상 인덱스를 추출해 list 객체로 만듦
    tried = user_rating[user_rating > 0].index.tolist()

    # 모든 도시명을 list 객체로 만듦
    beer_list = ratings_matrix.columns.tolist()

    # list comprehension으로 tried에 해당하는 도시는 beer_list에서 제외
    not_tried = [beer for beer in beer_list if beer not in tried]

    return not_tried


# 예측 평점 DataFrame에서 사용자 id 인덱스와 not_tried로 들어온 도시명 추출 후
# 가장 예측 평점이 높은 순으로 정렬


def recomm_beer_by_userid(pred_df, userId, not_tried, top_n):
    recomm_beer = pred_df.loc[userId,
                              not_tried].sort_values(ascending=False)[:top_n]
    return recomm_beer


def recomm_feature(df):

    ratings = df[['장소', '아이디', '평점']]
    # 피벗 테이블을 이용해 유저-아이디 매트릭스 구성
    ratings_matrix = ratings.pivot_table('평점', index='아이디', columns='장소')
    ratings_matrix.head(3)

    # fillna함수를 이용해 Nan처리
    ratings_matrix = ratings_matrix.fillna(0)

    # 유사도 계산을 위해 트랜스포즈
    ratings_matrix_T = ratings_matrix.transpose()

    # 아이템-유저 매트릭스로부터 코사인 유사도 구하기
    item_sim = cosine_similarity(ratings_matrix_T, ratings_matrix_T)

    # cosine_similarity()로 반환된 넘파이 행렬에 영화명을 매핑해 DataFrame으로 변환
    item_sim_df = pd.DataFrame(data=item_sim,
                               index=ratings_matrix.columns,
                               columns=ratings_matrix.columns)

    return item_sim_df


def recomm_beer(item_sim_df, beer_name):
    # 해당 도시와 유사도가 높은 도시 5개만 추천
    return item_sim_df[beer_name].sort_values(ascending=False)[1:10]


def recomm_detail(item_sim_df, detail):
    # 해당 도시와 유사도가 높은 도시 5개만 추천
    return item_sim_df[detail].sort_values(ascending=False)[1:10]


# 선택한 관광지 세션 저장
def ver2_select(request):
    beer_list = pd.read_csv('result.csv', encoding='utf-8', index_col=0)

    beer_list = beer_list['locate']

    text = {'beer_list': beer_list}

    login_session = request.session.get('login_session')

    if login_session == '':
        text['login_session'] = False
    else:
        text['login_session'] = True

    if request.method == 'POST':
        beer_name = request.POST.get('beer', '')
        request.session['tour'] = beer_name
        text['tour'] = request.session['tour']

    return render(request, 'beer/ver2.html', text)


# 찜하기
# class LikeProductView(View):

#     @Login_required
#     def post(self, request):
#         user_data = json.loads(request.body)

#         if not LikeProduct.objects.filter(product_id=user_data['product_id'],
#                                           user_id=request.user.id).exists():
#             LikeProduct.objects.create(
#                 user=request.user,
#                 product=Product.objects.get(id=user_data['product_id'])).save

#             return JsonResponse({'message': 'ADD_LIKE_PRODUCT'}, status=200)

#         delete_product = LikeProduct.objects.get(
#             product_id=user_data['product_id'], user_id=request.user.id)
#         delete_product.delete()

#         return JsonResponse({'message': 'DELETE_LIKE_PRODUCT'}, status=200)

#     @Login_required
#     def get(self, request):
#         like_list = []
#         like_product = LikeProduct.objects.filter(
#             user_id=request.user.id).prefetch_related("product")

#         for product in like_product:
#             data = {
#                 "id": product.product.id,
#                 "product_line": product.product.product_line,
#                 "name": product.product.name,
#                 "price": product.product.price,
#                 "sale_price": product.product.sale_price,
#                 "hash_tag": product.product.hash_tag,
#                 "images": product.product.image_set.first().image_url,
#                 "sale": product.product.productflag_set.first().sale_flag,
#                 "gift": product.product.productflag_set.first().gift_flag
#             }

#             like_list.append(data)

#         return JsonResponse({'like_list': like_list})


def cart_add(request, index):

    # 장바구니 추가
    product = Hotel.objects.get(pk=index)

    try:
        # 장바구니는 user 를 FK 로 참조하기 때문에 save() 를 하기 위해 user 가 누구인지도 알아야 함
        cart = Cart.objects.get(hotel=hotel.pk, user_id=request.user.pk)
        if cart:
            if cart.product.index == product.index:
                cart.quantity += 1
                cart.save()
    except CartItem.DoesNotExist:
        user = User.objects.get(pk=request.user.pk)
        cart = Cart()
        cart.save()
        return render(request, 'beer/ver_result.html')


# 세션에 저장된 관광지 가져와 계산
def ver2_session(request):
    ratings = pd.read_csv('merge.csv', encoding='utf-8', index_col=0)
    cluster_3 = pd.read_csv('대표군집클러스터링.csv', encoding='utf-8', index_col=0)
    cluster_all = pd.read_csv('전체도시클러스터링.csv', encoding='utf-8', index_col=0)

    # 세션 데이터 가져오기
    beer_name = request.session.get('tour')

    # 관광지 추천
    df = recomm_feature(ratings)

    result = recomm_beer(df, beer_name)
    result = result.index.tolist()

    # 로그인 세션 유지
    login_session = request.session.get('login_session')

    if login_session == '':
        request.session['login_session'] = False
    else:
        request.session['login_session'] = True

    # 숙박 시설 필터
    cost = request.GET.get('cost', '')
    sort = request.GET.get('sort', '')
    rating = request.GET.get('rating', '')
    rating1 = request.GET.get('rating1', '')
    distance = request.GET.get('distance', '')
    review = request.GET.get('review', '')

    if rating == 'rating':
        content_list = Hotel.objects.filter(
            place=result[0]).order_by('-rating')

    elif distance == 'distance':
        content_list = hotel1_distance_up = Hotel.objects.filter(
            place=result[0]).order_by('distance')

    elif cost == 'cost_down':
        content_list = Hotel.objects.filter(place=result[0]).order_by('-cost')

    elif cost == 'cost_up':
        content_list = Hotel.objects.filter(place=result[0]).order_by('cost')

    elif sort == 'hotell':
        content_list = Hotel.objects.filter(place=result[0],
                                            classfication='호텔')

    elif sort == 'hotell' and cost == 'cost_down':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='호텔').order_by('-cost')

    elif sort == 'hotell' and cost == 'cost_up':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='호텔').order_by('cost')

    elif sort == 'hotell' and rating == 'rating':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='호텔').order_by('-rating')

    elif sort == 'hotell' and distance == 'distance':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='호텔').order_by('distance')

    elif sort == 'guesthouse':
        content_list = Hotel.objects.filter(place=result[0],
                                            classfication='호텔')

    elif sort == 'guesthouse' and cost == 'cost_down':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='게스트하우스').order_by('-cost')

    elif sort == 'guesthouse' and cost == 'cost_up':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='게스트하우스').order_by('cost')

    elif sort == 'guesthouse' and rating == 'rating':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='게스트하우스').order_by('-rating')

    elif sort == 'guesthouse' and distance == 'distance':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='게스트하우스').order_by('distance')

    elif sort == 'hostel':
        content_list = Hotel.objects.filter(place=result[0],
                                            classfication='호스텔')

    elif sort == 'hostel' and cost == 'cost_down':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='호스텔').order_by('-cost')

    elif sort == 'hostel' and cost == 'cost_up':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='호스텔').order_by('cost')

    elif sort == 'hostel' and rating == 'rating':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='호스텔').order_by('-rating')

    elif sort == 'hostel' and distance == 'distance':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='호스텔').order_by('distance')

    elif sort == 'pension':
        content_list = Hotel.objects.filter(place=result[0],
                                            classfication='펜션')

    elif sort == 'pension' and cost == 'cost_down':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='펜션').order_by('-cost')

    elif sort == 'pension' and cost == 'cost_up':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='펜션').order_by('cost')

    elif sort == 'pension' and rating == 'rating':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='펜션').order_by('-rating')

    elif sort == 'pension' and distance == 'distance':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='펜션').order_by('distance')

    elif sort == 'motel':
        content_list = Hotel.objects.filter(place=result[0],
                                            classfication='모텔')

    elif sort == 'motel' and cost == 'cost_down':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='모텔').order_by('-cost')

    elif sort == 'motel' and cost == 'cost_up':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='모텔').order_by('cost')

    elif sort == 'motel' and rating == 'rating':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='모텔').order_by('-rating')

    elif sort == 'motel' and distance == 'distance':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='모텔').order_by('distance')

    elif sort == 'resort':
        content_list = Hotel.objects.filter(place=result[0],
                                            classfication='리조트')

    elif sort == 'resort' and cost == 'cost_down':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='리조트').order_by('-cost')

    elif sort == 'resort' and cost == 'cost_up':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='리조트').order_by('cost')

    elif sort == 'resort' and rating == 'rating':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='리조트').order_by('-rating')

    elif sort == 'resort' and distance == 'distance':
        content_list = Hotel.objects.filter(
            place=result[0], classfication='리조트').order_by('distance')

    else:
        content_list = Hotel.objects.filter(place=result[0])

    # 식당 정보 필터링
    if rating1 == 'rating1':
        content_list1 = Restaurant.objects.filter(
            place=result[0]).order_by('-rating')

    elif review == 'review':
        content_list1 = Restaurant.objects.filter(
            place=result[0]).order_by('-review')
    else:
        content_list1 = Restaurant.objects.filter(place=result[0])

    # 숙박시설 정보 Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(content_list, 10)
    posts = paginator.get_page(page)

    # 식당 정보 Pagination
    page1 = request.GET.get('page1', 1)
    paginator1 = Paginator(content_list1, 10)
    posts1 = paginator1.get_page(page1)

    return render(
        request, 'beer/ver_result.html', {
            'login_session': login_session,
            'result': result,
            'sort': sort,
            'cost': cost,
            'rating': rating,
            'distance': distance,
            'rating1': rating1,
            'review': review,
            'posts': posts,
            'posts1': posts1,
            'content_list': content_list,
            'content_list1': content_list1,
        })


def ver3_select(request):
    text = {}
    login_session = request.session.get('login_session')

    if login_session == '':
        text['login_session'] = False
    else:
        text['login_session'] = True

    # 디테일 세션 저장
    if request.method == 'POST':
        together = request.POST.get('together', '')
        request.session['together'] = together
        text['together'] = request.session['together']

        theme = request.POST.get('theme', '')
        request.session['theme'] = theme
        text['theme'] = request.session['theme']

        style = request.POST.get('style', '')
        request.session['style'] = style
        text['style'] = request.session['style']

        walking = request.POST.get('walking', '')
        request.session['walking'] = walking
        text['walking'] = request.session['walking']

        view = request.POST.get('view', '')
        request.session['view'] = view
        text['view'] = request.session['view']

        detail = [together, style, walking, theme, view]
        print(detail)
    return render(request, 'beer/ver3.html', text)


def ver3_session(request):

    # 디테일 세션 가져오기.
    together = request.session.get('together')
    theme = request.session.get('theme')
    style = request.session.get('style')
    walking = request.session.get('walking')
    view = request.session.get('view')
    detail = [together, theme, style, walking, view]
    login_session = request.session.get('login_session')

    cost = request.GET.get('cost', '')
    sort = request.GET.get('sort', '')
    rating = request.GET.get('rating', '')
    rating1 = request.GET.get('rating1', '')
    distance = request.GET.get('distance', '')
    review = request.GET.get('review', '')

    df_cluster = pd.read_csv('result.csv', encoding='utf-8', index_col=0)

    cst0_list = df_cluster.loc[df_cluster['Cluster'] == 0, 'locate'].tolist()

    cst1_list = df_cluster.loc[df_cluster['Cluster'] == 1, 'locate'].tolist()

    cst2_list = df_cluster.loc[df_cluster['Cluster'] == 2, 'locate'].tolist()

    cst3_list = df_cluster.loc[df_cluster['Cluster'] == 3, 'locate'].tolist()

    cst4_list = df_cluster.loc[df_cluster['Cluster'] == 4, 'locate'].tolist()

    cst5_list = df_cluster.loc[df_cluster['Cluster'] == 5, 'locate'].tolist()

    cst6_list = df_cluster.loc[df_cluster['Cluster'] == 6, 'locate'].tolist()

    cst7_list = df_cluster.loc[df_cluster['Cluster'] == 7, 'locate'].tolist()

    cst8_list = df_cluster.loc[df_cluster['Cluster'] == 8, 'locate'].tolist()

    cst9_list = df_cluster.loc[df_cluster['Cluster'] == 9, 'locate'].tolist()


    # 식당 정보 필터링
    if rating1 == 'rating1':
        content_list1 = Restaurant.objects.filter(
            place=result[0]).order_by('-rating')

    elif review == 'review':
        content_list1 = Restaurant.objects.filter(
            place=result[0]).order_by('-review')
    else:
        content_list1 = Restaurant.objects.filter(place=result[0])

    # 숙박시설 정보 Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(content_list, 10)
    posts = paginator.get_page(page)

    # 식당 정보 Pagination
    page1 = request.GET.get('page1', 1)
    paginator1 = Paginator(content_list1, 10)
    posts1 = paginator1.get_page(page1)

    # 관광지 Pagination
    page2 = request.GET.get('page2', 1)
    paginator2 = Paginator(result, 10)
    posts2 = paginator2.get_page(page2)
    return render(
        request, 'beer/ver_result.html', {
            'login_session': login_session,
            'result': result,
            'sort': sort,
            'cost': cost,
            'rating': rating,
            'distance': distance,
            'posts': posts,
            'posts1': posts1,
            'content_list': content_list,
            'content_list1': content_list1,
            'posts2': posts
        })
