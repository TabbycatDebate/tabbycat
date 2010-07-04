def main():
    from debate.views import get_wordpress_client
    from django.conf import settings
    from debate import wordpresslib

    client = get_wordpress_client()
    post = wordpresslib.WordPressPost()
    post.title = 'Break'
    post.description = open('break.html').read()
    post.categories = (settings.WORDPRESS_DRAW_CATEGORY_ID,)
    client.newPost(post, False)

if __name__ == '__main__':
    main()

