import json
from rest_framework.renderers import JSONRenderer


class ArticleJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if data is not None:

            if isinstance(data, dict):
                return json.dumps({
                    'article': data
                })
            return json.dumps({
                'articles': data,
                'articlesCount': len(data)
            })
        return json.dumps({
            "article": 'No article found.'
        })

class CommentJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        
        if isinstance(data, dict):
            errors = data.get('errors', None)
            is_active = data.get('is_active', None)

            if errors is not None:
                
                return super(CommentJSONRenderer, self).render(data)

            if is_active is not None:
                data = self.filter_data(data)

            return json.dumps({
                'comment': data
            })

        for comment in data:
            comment = self.filter_data(comment)

        return json.dumps({
                'comments': data,
                'commentsCount': len(data)
            })

    def filter_data(self, data):
        if data['is_active'] == False:
            del data['is_active']
            del data['article']
            del data['author']
            del data['id']
            del data['createdAt']
            del data['updatedAt']
            del data['body']
            data['comment'] = "deleted"
        else:
            del data['is_active']
            del data['article']
            data['author'] = {
                        "username": data['author']['username'],
                        "bio": data['author']['bio'],
                        "image": data['author']['avatar'],
                        "following": data['author']['following']
                    }

        if len(data['subcomments']) > 0:
            for comment in data['subcomments']:
                comment = self.filter_data(comment)

        return data

