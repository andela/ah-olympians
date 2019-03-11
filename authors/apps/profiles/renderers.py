import json

from rest_framework.renderers import JSONRenderer


class ProfileJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        # If the view throws an error (such as the user can't be authenticated
        # or something similar), `data` will contain an `errors` key. We want
        # the default JSONRenderer to handle rendering errors, so we need to
        # check for this case.
        errors = data.get('errors', None)
        token = data.get('token', None)

        if errors is not None:
            # As mentioned about, we will let the default JSONRenderer handle
            # rendering errors.
            return super(ProfileJSONRenderer, self).render(data)

        if token is not None and isinstance(token, bytes):
            # We will decode `token` if it is of type
            # bytes.
            data['token'] = token.decode('utf-8')

        # Append Cloudinary URL prefix to stored avatar link
        if data.get("avatar"):
            avatar_prefix = "https://res.cloudinary.com/jumakahiga/"
            data["avatar"] = avatar_prefix + data["avatar"]

        # Finally, we can render our data under the "user" namespace.
        return json.dumps({
            'profile': data
        })
