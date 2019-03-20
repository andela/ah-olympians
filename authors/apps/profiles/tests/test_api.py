"""Test API endpoints"""
import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ...authentication.models import User
from ..models import UserProfile

# tests for Endpoints


class ProfileTest(APITestCase):
    client = APIClient()

    def setUp(self):
        # add test data
        self.user = {
            "user": {
                "email": "caro@yahoo.com",
                "username": "caro",
                "password": "07921513542"
            }
        }

        self.profile = {
            "bio": "am fantastic",
            "interests": "football",
            "favorite_quote": "Yes we can",
            "mailing_address": "P.O BOX 1080",
            "website": "http://www.web.com",
            "active_profile": True
        }

        # create user
        self.client.post('/api/users/', self.user, format='json')
        # user login
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

    def test_create_profile(self):
        """
        test create profile
        """
        response = self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["interests"], "football")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_existing_profile(self):
        """
        test create profile  yet it already exists
        """
        #create profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        #create profile again
        response = self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["message"], "A user with this profile already exists")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_profile_while_deactivated(self):
        """
        test create profile  when profile is deactivated
        """
        #create profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        #Deactivate profile
        response = self.client.put(
            '/api/profile/deactivate_profile/', format='json')

        #create profile again
        response = self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["message"],
            "You deactivated your profile. Please activate to continue")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_profile(self):
        """
        test view profile
        """
        # create profile
        response = self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        # view profile
        current_user = User.objects.get(username='caro')
        response = self.client.get(
            '/api/profile/view_profile/' + str(current_user.id), format='json')
        result = json.loads(response.content)

        self.assertIn("football", str(result["profile"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_profiles_created(self):
        """
        test view when no profiles exist
        """
        # view profile
        response = self.client.get(
            '/api/profile/view_profiles/', format='json')
        result = json.loads(response.content)

        self.assertIn("No user profiles found", str(result))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_all_profiles(self):
        """
        test view profile
        """
        # create profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        # view profile
        response = self.client.get(
            '/api/profile/view_profiles/', format='json')
        result = json.loads(response.content)

        self.assertIn("caro", str(result["profile"]["profiles"]))
        self.assertEqual(1, len(result["profile"]["profiles"].items()))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_profile_not_created(self):
        """
        test view profile that has not been created
        """
        # create profile
        response = self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        # view profile
        response = self.client.get(
            '/api/profile/view_profile/16', format='json')
        result = json.loads(response.content)

        self.assertIn("User profile does not exist", str(result))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_profile_with_invalid_id(self):
        """
        test view profile with an id that is not integer
        """
        # create profile
        response = self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        # view profile
        response = self.client.get(
            '/api/profile/view_profile/caro', format='json')
        result = json.loads(response.content)

        self.assertIn("User ID must be an integer", str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_profile(self):
        """
        test edit profile
        """
        # create profile
        response = self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        # edit profile
        self.profile["interests"] = "music"

        response = self.client.put(
            '/api/profile/edit_profile/', self.profile, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["interests"], "music")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_edit_non_existent_profile(self):
        """
        test editing a profile that does not exist
        """
        # edit profile
        self.profile["interests"] = "music"
        
        response = self.client.put(
            '/api/profile/edit_profile/', self.profile, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["message"],
            "User profile not found. Please create one")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_profile(self):
        """
        test deactivating a profile
        """
        # create profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')
        
        response = self.client.put(
            '/api/profile/deactivate_profile/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["active_profile"],
            False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deactivate_nonexistent_profile(self):
        """
        test deactivating a non-existent profile
        """
        
        response = self.client.put(
            '/api/profile/deactivate_profile/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["message"],
            "User profile not found")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_profile_already_deactivated(self):
        """
        test deactivating already deactivated profile
        """
        # create profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')
        # deactivate
        self.client.put(
            '/api/profile/deactivate_profile/', format='json')
        
        response = self.client.put(
            '/api/profile/deactivate_profile/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["message"],
            "You deactivated your profile. Please activate to continue")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_profile(self):
        """
        test activating a profile
        """
        # create profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')
        # deactivate
        self.client.put(
            '/api/profile/deactivate_profile/', format='json')
        
        response = self.client.put(
            '/api/profile/activate_profile/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["active_profile"],
            True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_activate_profile_already_activated(self):
        """
        test activating already active profile
        """
        # create profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')
        
        response = self.client.put(
            '/api/profile/activate_profile/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["message"],
            "Your profile is already active and viewable by other users")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deactivate_nonexistent_profile(self):
        """
        test activating a non-existent profile
        """
        
        response = self.client.put(
            '/api/profile/activate_profile/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["message"],
            "User profile not found")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_upload_at_edit(self):
        """
        test uploading an avatar that is not an image
        """
        # edit profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        response = self.client.put(
            '/api/profile/edit_profile/', {"avatar": "bad.py"}, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["message"],
            "Only '.png', '.jpg', '.jpeg' files are accepted")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestFollowUnFollow(APITestCase):
    client = APIClient()

    def setUp(self):
        self.user = {
            "user": {
                "email": "caro@yahoo.com",
                "username": "caro",
                "password": "07921513542"
            }
        }

        self.profile = {
            "bio": "am fantastic",
            "interests": "football",
            "favorite_quote": "Yes we can",
            "mailing_address": "P.O BOX 1080",
            "website": "http://www.web.com",
            "active_profile": True
        }

        self.user2 = {
            "user": {
                "email": "kibet@yahoo.com",
                "username": "kibet",
                "password": "07921513542"
            }
        }

        self.profile2 = {
            "bio": "yeah",
            "interests": "Money",
            "favorite_quote": "Yes we can",
            "mailing_address": "P.O BOX 1080",
            "website": "http://www.web.com",
            "active_profile": True
        }

        self.user3 = {
            "user": {
                "email": "winnie@yahoo.com",
                "username": "winnie",
                "password": "07921513542"
            }
        }

        self.profile3 = {
            "bio": "Whaaat",
            "interests": "Fun",
            "favorite_quote": "Yes we can",
            "mailing_address": "P.O BOX 1080",
            "website": "http://www.web.com",
            "active_profile": True
        }



        # create users
        result = self.client.post('/api/users/', self.user, format='json')
        result = self.client.post('/api/users/', self.user2, format='json')
        result = self.client.post('/api/users/', self.user3, format='json')
        # create profile
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post('/api/profile/create_profile/', self.profile, format='json')
    
    def test_follow_profile(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post('/api/profile/create_profile/', self.profile2, format='json')

        target_profile = User.objects.get(username="caro")
        response = self.client.post('/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"],
            "{}, you have successfully followed {}".format(self.user2["user"]["username"],
                self.user["user"]["username"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unfollow_profile(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post('/api/profile/create_profile/', self.profile2, format='json')

        target_profile = User.objects.get(username="caro")
        self.client.post('/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        response = self.client.delete('/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"],
            "{}, you have successfully unfollowed {}".format(self.user2["user"]["username"],
                self.user["user"]["username"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_follow_profile_wrong_id(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post('/api/profile/create_profile/', self.profile2, format='json')

        target_profile = "n"
        response = self.client.post('/api/profile/view_profile/' + str(target_profile) + '/follow/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"],
            "User ID must be an integer")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_nonexistent_profile(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post('/api/profile/create_profile/', self.profile2, format='json')

        target_profile = User.objects.get(username="winnie")
        response = self.client.post('/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"],
            "We did not find such a profile.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_profile_twice(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post('/api/profile/create_profile/', self.profile2, format='json')

        target_profile = User.objects.get(username="caro")
        self.client.post('/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        response = self.client.post('/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"],
            "{}, you already follow {}".format(self.user2["user"]["username"],
                self.user["user"]["username"]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_profile_twice(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post('/api/profile/create_profile/', self.profile2, format='json')

        target_profile = User.objects.get(username="caro")
        self.client.post('/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        self.client.delete('/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        response = self.client.delete('/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"],
            "{}, you do not follow {}".format(self.user2["user"]["username"],
                self.user["user"]["username"]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_self(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post('/api/profile/create_profile/', self.profile2, format='json')

        target_profile = User.objects.get(username="kibet")
        response = self.client.post(
            '/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"],
            "You cannot follow yourself.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_self(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post(
            '/api/profile/create_profile/', self.profile2, format='json')

        target_profile = User.objects.get(username="kibet")
        response = self.client.delete(
            '/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"],
            "You cannot unfollow yourself.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_following_list(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post(
            '/api/profile/create_profile/', self.profile2, format='json')

        target_profile = User.objects.get(username="caro")
        response = self.client.post(
            '/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')

        response = self.client.get(
            '/api/profile/view_profile/following/', format='json')
        result = json.loads(response.content)

        self.assertIn("caro", result["profile"]["following"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_followers_list(self):
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        result = self.client.post(
            '/api/profile/create_profile/', self.profile2, format='json')

        target_profile = User.objects.get(username="caro")
        response = self.client.post(
            '/api/profile/view_profile/' + str(target_profile.id) + '/follow/', format='json')

        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)
        token = result["user"]["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.get(
            '/api/profile/view_profile/followers/', format='json')
        result = json.loads(response.content)

        self.assertIn("kibet", result["profile"]["followers"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        


   