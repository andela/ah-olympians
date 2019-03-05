"""Test API endpoints"""
import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ...authentication.models import User

# tests for Endpoints


class UserTest(APITestCase):
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
   