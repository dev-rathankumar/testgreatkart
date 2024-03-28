from .models import Category

# CONTEXT PROCESSORS FOR CATEGORY APP
# This context processor will pass the category links to all templates
# without having to pass it to the context of every view


# LINK TO CATEGORY PAGES FOR NAVIGATION
def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)