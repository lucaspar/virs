from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib import messages
from django.template import loader
from django.conf import settings

from cop.invertedIndex import InvertedIndex
from cop.vectorSpaceModel import VectorSpaceModel
from .storage import handle_uploaded_files
from .forms import CollectionUploadForm
from .decorators import check_recaptcha
from .models import Collection

import os
import json
import urllib

SEL_COLLECTION_COOKIE = 'sel_collection'

# ----------------------------------------
#             AUXILIAR METHODS

# Handles POST request of collection selection
def handleCollectionPost(request):
    current_collection = request.POST.get('collection_selector')
    response = redirect(request.path_info)
    response.set_cookie(SEL_COLLECTION_COOKIE, current_collection)
    return response

# Builds a collection's filesystem path from cookie
def buildCollectionPath(request):
    current_collection = request.COOKIES.get(SEL_COLLECTION_COOKIE, False)
    if current_collection:
        # TODO: validate collection uuid from cookie
        collection_path = os.path.join(settings.COLLECTION_UPLOADS, current_collection)
    else:
        collection_path = "/virs/collection/"       # default fallback
    return collection_path

def standardResponse(request, context, template_path):
    rendered = render_to_string(template_path, context, request=request)
    response = HttpResponse(rendered)
    return response

# ----------------------------------------
#               VIEW METHODS

# Home view
def home(request):

    context = {
        'title': 'Visualization and Information Retrieval System',
    }

    return render(request, 'vsm/index.html', context)


# ----------------------------------------
# Handle user uploads (GET and POST)
@check_recaptcha
def upload(request):

    # handle POST request
    if request.method == 'POST':
        form = CollectionUploadForm(request.POST, request.FILES)
        file_list = request.FILES.getlist('files')

        # check form validation
        if form.is_valid() and request.recaptcha_is_valid:

            model = form.save(commit=False)
            model.corpus_size = len(file_list)

            # upload files
            handle_uploaded_files(file_list, dir_name=str(model.id))

            # save model to database
            model.save()
            messages.success(request, 'Nova coleção adicionada')

            return redirect('home')

    # handle other requests or POST failure
    context = {
        'title': 'Upload de Coleção',
        'GOOGLE_RECAPTCHA_PUBLIC_KEY': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    # build response
    return standardResponse(request, context, 'vsm/upload.html')


# ----------------------------------------
# Shows a collection's Postings List
def postings(request):

    # load collection
    ii = InvertedIndex("/virs/collection/")
    postings = ii.generatePostingsList()

    # pass computed data in context
    context = {
        'title': 'Arquivo Invertido',
        'postings' : postings,
        'collections': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
    }

    # build response
    return standardResponse(request, context, 'vsm/postings.html')

# ----------------------------------------
# Shows a collection's Vector Space Model
def vsm(request):

    # if POST request, set cookie and redirect to GET request
    if request.method == 'POST':
        return handleCollectionPost(request)

    vsm = VectorSpaceModel( buildCollectionPath(request) )
    vsm_table = vsm.generateVectorSpaceModel()

    # form table headers
    headers = []
    for term, value in vsm_table.items():
        for header, v in value.items():
            if header is 'tf' or header is 'tfidf':
                for c in range(0, len(v)):
                    headers.append(header + ' ' + str(c))
            else:
                headers.append(header)
        break

    # pass computed data in context
    context = {
        'title': 'Modelo Vetorial',
        'collections': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
        'vsm': vsm_table,
        'headers': headers,
    }

    # build response
    return standardResponse(request, context, 'vsm/vsm.html')


# ----------------------------------------
# Handles user searches over a collection
def query(request):

    context = {
        'title': 'Consulta',
        'collections': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
    }

    # build response
    return standardResponse(request, context, 'vsm/query.html')
