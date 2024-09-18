# roomio/search/views.py
from django.db import connection
from django.shortcuts import redirect, render

from home.models import Favorite
from .forms import SearchForm, SearchZipRoomForm, InterestSearchForm
from add_post.models import ApartmentUnit, ApartmentBuilding

def search_home(request):
    if not request.user.is_authenticated:
        return redirect("login:login")
    
    form = SearchForm(request.POST or None)
    units_data = []

    if request.method == 'POST' and form.is_valid():
        company_name = form.cleaned_data['company_name']
        building_name = form.cleaned_data['building_name']
        apply_rent_filter = form.cleaned_data.get('apply_rent_filter', False)
        min_rent = form.cleaned_data.get('min_rent', 0)
        max_rent = form.cleaned_data.get('max_rent', 10000)  # Defaulting to a high number if no filter is to be applied

        raw_query = """
            SELECT au.id, au.unit_number, au.monthly_rent, au.square_footage, au.available_date_for_move_in,
                   ab.id AS building_id, ab.building_name, ab.company_name, ab.address_number, ab.address_street,
                   ab.address_city, ab.address_state, ab.address_zip_code
            FROM add_post_apartmentunit AS au
            INNER JOIN add_post_apartmentbuilding AS ab ON au.building_id = ab.id
            WHERE ab.company_name LIKE %s AND ab.building_name LIKE %s
        """

        parameters = [company_name, building_name]

        if apply_rent_filter:
            raw_query += " AND au.monthly_rent BETWEEN %s AND %s"
            parameters += [min_rent, max_rent]

        with connection.cursor() as cursor:
            cursor.execute(raw_query, parameters)
            units = cursor.fetchall()
            cursor.execute("SELECT unit_id FROM home_favorite WHERE user_id = %s", [request.user.id])
            favorites = cursor.fetchall()
            favorite_ids = [item[0] for item in favorites]

        units_data = [{
            'unit': {
                'id': unit[0],
                'unit_number': unit[1],
                'monthly_rent': unit[2],
                'square_footage': unit[3],
                'available_date_for_move_in': unit[4],
                'building': {
                    'id': unit[5],
                    'building_name': unit[6],
                    'company_name': unit[7],
                    'address_number': unit[8],
                    'address_street': unit[9],
                    'address_city': unit[10],
                    'address_state': unit[11],
                    'address_zip_code': unit[12]
                }
            },
            'is_favourited': unit[0] in favorite_ids
        } for unit in units]

        context = {
            "searchForm": form,
            "units_data": units_data
        }
    else:
        context = {
            "searchForm": form,
            "units_data": []
        }

    return render(request, 'search/search_page.html', context)

def search_interest(request):
    if not request.user.is_authenticated:
        return redirect("login:login")
    
    form = InterestSearchForm(request.POST or None)
    interests_data = []

    if request.method == 'POST' and form.is_valid():
        roommateCnt = form.cleaned_data.get('roommateCnt')
        move_in_date = form.cleaned_data.get('move_in_date')

        # Start building the raw SQL query
        raw_query = """
        SELECT i.id, 
       i.roommate_count, 
       i.move_in_date, 
       a.unit_number, 
       ab.building_name,
       ab.address_number,
       ab.address_street, 
       ab.address_city,
       ab.address_state,
       ab.address_zip_code,
       u.username,
       a.id
       FROM home_interest i
       INNER JOIN add_post_apartmentunit a ON i.unit_id = a.id
       INNER JOIN add_post_apartmentbuilding ab ON a.building_id = ab.id
       INNER JOIN login_user u ON i.user_id = u.id
       WHERE 1=1
        """

        # Adding conditions to the SQL query
        params = []
        if roommateCnt is not None:
            raw_query += " AND i.roommate_count = %s"
            params.append(roommateCnt)
        if move_in_date:
            raw_query += " AND i.move_in_date = %s"
            params.append(move_in_date)

        # Execute the raw SQL query
        with connection.cursor() as cursor:
            cursor.execute(raw_query, params)
            result = cursor.fetchall()

            # Fetch results and format them into a list of dictionaries
            interests_data = [{
                'interest_id': row[0],
                'roommate_count': row[1],
                'move_in_date': row[2],
                'unit_number': row[3],
                'building_name':row[4],
                'address_number':row[5],
                'address_street':row[6],
                'address_city':row[7],
                'address_state':row[8],
                'address_zip_code':row[9],
                'username': row[10],
                'unit_id': row[11]
                
            } for row in result]
        print(interests_data)
    context = {
        'form': form,
        'interests_data': interests_data
    }

    return render(request, 'search/search_interest.html', context)


def search_zip(request):
    if not request.user.is_authenticated:
        return redirect("login:login")
    
    form = SearchZipRoomForm(request.POST or None)
    units_data = []

    if request.method == 'POST' and form.is_valid():
        zip_code = form.cleaned_data.get('zip_code', '')
        bedrooms = form.cleaned_data.get('rooms', 1)
        bathrooms = form.cleaned_data.get('bathrooms',1)


        raw_query = """
            SELECT AVG(au.monthly_rent) AS average_rent
            FROM add_post_apartmentunit AS au
            JOIN add_post_apartmentbuilding AS ab ON au.building_id = ab.id
            JOIN (
                SELECT unit_id, 
                    SUM(CASE WHEN name LIKE 'bedroom%%' THEN 1 ELSE 0 END) AS bedroom_count,
                    SUM(CASE WHEN name LIKE 'bathroom%%' THEN 1 ELSE 0 END) AS bathroom_count
                FROM add_post_room
                GROUP BY unit_id
                HAVING SUM(CASE WHEN name LIKE 'bedroom%%' THEN 1 ELSE 0 END) = %s
                AND SUM(CASE WHEN name LIKE 'bathroom%%' THEN 1 ELSE 0 END) = %s
                ) AS rooms ON rooms.unit_id = au.id
            WHERE ab.address_zip_code LIKE %s
            GROUP BY ab.address_zip_code;
        """

        with connection.cursor() as cursor:
            cursor.execute(raw_query, [bedrooms, bathrooms, f'%{zip_code}%'])
            # cursor.execute(raw_query, [1, 1, 14287])
            units = cursor.fetchall()

            # Get list of unit IDs that are favorited by the user
            cursor.execute("SELECT unit_id FROM home_favorite WHERE user_id = %s", [request.user.id])
            favorites = cursor.fetchall()
            favorite_ids = [item[0] for item in favorites]

        # Creating a list of units with favorite status
        units_data = [{
            'unit': {
                'average_rent': unit[0],
            },
            'is_favourited': unit[0] in favorite_ids
        } for unit in units]

        context = {
            "searchZipForm": form,
            "units_data": units_data
        }
    else:
        context = {
            "searchZipForm": form,
            "units_data": []  # Ensure units_data is always defined
        }

    return render(request, 'search/search_zip.html', context)
