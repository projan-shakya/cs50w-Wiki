from django.shortcuts import render
import markdown
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from . import util
import encyclopedia
import random

class editForm(forms.Form):
    title = forms.CharField(label = "Title", widget= forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    text = forms.CharField(label = "Content", widget= forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 10}))
    edit = forms.BooleanField(initial = False, widget = forms.HiddenInput(), required = False)

class NewEntryForm(forms.Form):
    title = forms.CharField(label = "New Entry", widget= forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(label = "Content", widget= forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 10}))
    edit = forms.BooleanField(initial = False, widget = forms.HiddenInput(), required = False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def convertToHtml(title):
    entry = util.get_entry(title)

    html = markdown.markdown(entry) if entry else None #convert markdown to html if it exists

    return html

def entry(request, title):
    page = util.get_entry(title) 

    if page is None:
        return render(request, "encyclopedia/NoPage.html", {
            "entryTitle": title
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entries": convertToHtml(title),
            "entryTitle": title
        })

def search(request):

    if request.method == 'GET':
        input = request.GET.get('q')
        entries = util.list_entries()
        searched_pages = []

        for entry in entries:
            if input.upper() == entry.upper():
                return render(request, "encyclopedia/entry.html", {
                    "entryTItle": input,
                    "entries": convertToHtml(input)
                })
        
        for entry in entries:
            if input.upper() in entry.upper():        
                searched_pages.append(entry)
        
        if searched_pages == []:
            return render(request, "encyclopedia/noResult.html",{
                "result": input
            })

        return render(request, "encyclopedia/searchPage.html", {
                    "entries": searched_pages,
                    "result" : input
                })


def newEntry(request):
    allPages = util.list_entries()
    if request.method == "POST":
        form = NewEntryForm(request.POST)

        if form.is_valid():
            exists = False
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            for entry in allPages:
                if title.lower() == entry.lower():
                    exists = True
            if exists == True:
                return render(request, "encyclopedia/existingPage.html",{
                    "entryTitle": title
                })
            else:
                util.save_entry(title, content)
            
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries()
            })


    return render(request, "encyclopedia/new.html", {
        "form" : NewEntryForm()
    })

def randomPage(request):
    entries = util.list_entries()
    rand = random.choice(entries)

    return render(request, "encyclopedia/entry.html",{
		"entries": convertToHtml(rand),
		"entryTitle":rand
	})

def editPage(request, title):
    if request.method == "POST":
        form = editForm(request.POST)

    text = util.get_entry(title)

    return render(request, "encyclopedia/editPage.html", {
        "form" : editForm({"title": title, "text": text}),
        "entryTitle": title
    })

def saveEdit(request):
    if request.method == "POST":
        form = editForm(request.POST)
        title = request.POST['title']
        content = request.POST['text']

        util.save_entry(title, content)

    return render(request, "encyclopedia/entry.html", {
        "entries": convertToHtml(title),
        "entryTitle": title
    })