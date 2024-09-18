

import json
from django.db import connection
from django.utils import timezone
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Favorite, Interest
from .forms import InterestForm
from django.views.decorators.http import require_POST


from add_post.models import ApartmentBuilding, ApartmentUnit, PetPolicy
from user_profile.models import Pet

# Create your views here.

from .models import Interest  # Adjust the import path based on your project structure


def home_page(request):
    if not request.user.is_authenticated:
        return redirect("login:login")

    with connection.cursor() as cursor:
        # Fetching unit details along with building details
        cursor.execute("""
            SELECT au.id, au.unit_number, au.monthly_rent, au.square_footage, au.available_date_for_move_in,
                   ab.id AS building_id, ab.building_name, ab.company_name, ab.address_number, ab.address_street,
                   ab.address_city, ab.address_state, ab.address_zip_code
            FROM add_post_apartmentunit AS au
            INNER JOIN add_post_apartmentbuilding AS ab ON au.building_id = ab.id
        """)
        units = cursor.fetchall()

        # Fetching favorite unit IDs for the current user
        cursor.execute("SELECT unit_id FROM home_favorite WHERE user_id = %s", [request.user.id])
        favorites = cursor.fetchall()
        favorite_ids = [item[0] for item in favorites]

    # Creating units data with unit and building details
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
                'address_zip_code': unit[12],
                
            }
        },
        'is_favourited': unit[0] in favorite_ids
    } for unit in units]

    return render(request, 'home/home_page.html', {'units_data': units_data})



def toggle_favourite(request, unitId):
    if not request.user.is_authenticated:
        return redirect("login:login")
        # return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM add_post_apartmentunit WHERE id = %s", [unitId])
        unit_exists = cursor.fetchone()
        if not unit_exists:
            return JsonResponse({'status': 'error', 'message': 'Unit not found'}, status=404)

        cursor.execute("SELECT id FROM home_favorite WHERE user_id = %s AND unit_id = %s", [request.user.id, unitId])
        favorite = cursor.fetchone()
        
        if favorite:
            cursor.execute("DELETE FROM home_favorite WHERE id = %s", [favorite[0]])
            is_favourited = False
        else:
            cursor.execute("INSERT INTO home_favorite (user_id, unit_id, created_at) VALUES (%s, %s, %s)", [request.user.id, unitId, timezone.now()])
            is_favourited = True

        return JsonResponse({'status': 'success', 'is_favourited': is_favourited})




def logout(request):
    # Clear Django session data
    request.session.clear()
    return redirect("login:login")

def unit_details(request, unit_id):
    if not request.user.is_authenticated:
        return redirect("login:login")

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM add_post_apartmentunit WHERE id = %s", [unit_id])
        unit = cursor.fetchone()
        if not unit:
            return redirect("404")
        
        cursor.execute("""
            SELECT au.id, au.unit_number, au.monthly_rent, au.square_footage, au.available_date_for_move_in,
                   ab.id, ab.building_name, ab.company_name, ab.address_number, ab.address_street,
                   ab.address_city, ab.address_state, ab.address_zip_code
            FROM add_post_apartmentunit AS au
            INNER JOIN add_post_apartmentbuilding AS ab ON au.building_id = ab.id
            WHERE au.id = %s
        """, [unit_id])
        result = cursor.fetchone()

        if not result:
            return redirect("404")

        unit = {
            'id': result[0],
            'unit_number': result[1],
            'monthly_rent': result[2],
            'square_footage': result[3],
            'available_date_for_move_in': result[4],
            'building': {
                'id': result[5],
                'building_name': result[6],
                'company_name': result[7],
                'address_number': result[8],
                'address_street': result[9],
                'address_city': result[10],
                'address_state': result[11],
                'address_zip_code': result[12]
            }
        }

        cursor.execute("SELECT pet_type, pet_size FROM user_profile_pet WHERE owner_id = %s", [request.user.id])
        user_pets = cursor.fetchall()

        pet_policies=[]
        print()
        if user_pets:
            for i in range(len(user_pets)):
                print(user_pets[i][0] ,"-", user_pets[i][1] )
                cursor.execute("""
                SELECT pp.pet_type, pp.pet_size, pp.is_allowed, pp.registration_fee, pp.monthly_fee
                FROM add_post_petpolicy pp
                JOIN user_profile_pet pet ON pp.pet_type = pet.pet_type AND pp.pet_size = pet.pet_size
                WHERE pp.apartment_building_id = %s AND pp.pet_type LIKE %s AND pp.pet_size LIKE %s
            """, [unit['building']['id'], user_pets[i][0], user_pets[i][1]])
                row = cursor.fetchone()
                
                rows = cursor.fetchall()
                # print(rows)
                for row in rows:
                    pet_policies.append({
                        'pet_type': row[0],
                        'pet_size': row[1],
                        'allowed': row[2],
                        'registration_fee': row[3],
                        'monthly_fee': row[4]
                    })

        

        # Fetch other interests excluding the current user
        cursor.execute("""
            SELECT u.first_name, u.last_name, i.move_in_date, i.roommate_count
            FROM home_interest i
            JOIN login_user u ON i.user_id = u.id
            WHERE i.unit_id = %s AND i.user_id != %s
        """, [unit_id, request.user.id])
        other_interests = [{
            'user': {
                'first_name': row[0],
                'last_name': row[1]
            },
            'move_in_date': row[2],
            'roommate_count': row[3]
        } for row in cursor.fetchall()]

        cursor.execute("""
            SELECT a.type, a.description
            FROM add_post_amenities a
            JOIN add_post_apartmentamenities aa ON a.id = aa.amenity_id
            WHERE aa.unit_id = %s
        """, [unit_id])
        amenities = [{'type': row[0], 'description': row[1]} for row in cursor.fetchall()]

    context = {
        'unit': unit,
        'pet_policies': pet_policies,
        'other_interests': other_interests,
        'amenities': amenities
    }
    return render(request, 'home/unit_detail.html', context)


def create_interest(request, unit_id):
    if not request.user.is_authenticated:
        return redirect('login:login')

    if request.method == 'POST':
        form = InterestForm(request.POST)
        if form.is_valid():
            move_in_date = form.cleaned_data['move_in_date']
            roommate_count = form.cleaned_data['roommate_count']

            # Now we need to insert these values into the database using raw SQL
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO home_interest (user_id, unit_id, move_in_date, roommate_count)
                    VALUES (%s, %s, %s, %s)
                """, [request.user.id, unit_id, move_in_date, roommate_count])

            return redirect('home:home')  # Redirect to the home page after successfully creating the interest
        else:
            # If the form is not valid, we continue to display the form with errors
            return render(request, 'home/create_interest.html', {'form': form})
    else:
        # If not a POST request, just display the form
        form = InterestForm()
        return render(request, 'home/create_interest.html', {'form': form})

def favorite_list(request):
    if not request.user.is_authenticated:
        return redirect('login:login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT f.unit_id, u.unit_number, u.monthly_rent, u.square_footage, u.available_date_for_move_in,
                   b.id, b.building_name, b.company_name, b.address_number, b.address_street, 
                   b.address_city, b.address_state, b.address_zip_code
            FROM home_favorite f
            JOIN add_post_apartmentunit u ON f.unit_id = u.id
            JOIN add_post_apartmentbuilding b ON u.building_id = b.id
            WHERE f.user_id = %s
        """, [request.user.id])
        favorites = [{
            'unit_id': row[0],
            'unit_number': row[1],
            'monthly_rent': row[2],
            'square_footage': row[3],
            'available_date_for_move_in': row[4],
            'building': {
                'id': row[5],
                'building_name': row[6],
                'company_name': row[7],
                'address_number': row[8],
                'address_street': row[9],
                'address_city': row[10],
                'address_state': row[11],
                'address_zip_code': row[12]
            }
        } for row in cursor.fetchall()]

    favorite_unit_ids = [fav['unit_id'] for fav in favorites]
    
    return render(request, 'home/favorite_page.html', {
        'favorites': favorites,
        'favorite_unit_ids': favorite_unit_ids,
        # 'is_favourited': favorites[0] in favorite_unit_ids
        'is_favourited': bool(favorites and favorites[0]['unit_id'] in favorite_unit_ids)
    })