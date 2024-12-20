from django.shortcuts import render,redirect, get_object_or_404
from .models import *
from.forms import*
from bs4 import BeautifulSoup
import requests
from django.contrib import messages



def home_view(request, tag = None):
    if tag:
        posts = Post.objects.filter(tags__slug=tag)
        tag = get_object_or_404(Tag, slug=tag)
    else:
         posts = Post.objects.all()
        
    categories = Tag.objects.all() 
    context = {
        'posts': posts,
        'categories': categories,
        'tag': tag
    }   
    return render(request, 'aposts/home.html', context)



def post_create_view(request):
    form = PostCreateForm()
    
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post= form.save(commit = False)
            website = requests.get(form.data['url'])
            
            sourcecode = BeautifulSoup(website.text, 'html.parser')
            
            find_image = sourcecode.select('meta[content^="https://live.staticflickr.com/"]')
            
            image = find_image[0]['content']
            post.image = image
            
            find_title = sourcecode.select('h1.photo-title')
            title = find_title[0].text.strip()
            post.title = title
            
            post.author = request.user
            
            find_artist = sourcecode.select('a.owner-name')
            artist = find_artist[0].text.strip() 
            post.artist = artist
            
            post.save()
            form.save_m2m()
            return redirect('home')
    return render(request, 'aposts/post_create.html', {'form': form})


def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    if request.method == "POST":
        post.delete()
        messages.success(request, 'Post deleted')
        return redirect('home')
    return render(request, 'aposts/post_delete.html',{'post':post})

def post_edit_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    form = PostEditForm( instance=post)
    
    if request.method == "POST":
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid:
            form.save()
            messages.success(request, 'Post updated')
            return redirect('home')
            
            
    context = {
        'post' : post,
        'form' : form
    }
    return render(request, 'aposts/post_edit.html',context)

def post_page_view(request, pk):
    post = Post.objects.get(id=pk)
    post = get_object_or_404(Post, id=pk)
    commentform = CommentCreateForm()
    replyform = ReplyCreateForm()
    
    context = {
        'post' : post,
        'commentform' : commentform,
        'replyform' : replyform,
    }
        
    return render(request, 'aposts/post_page.html',context)

def comment_sent(request, pk):
    post = get_object_or_404(Post, id=pk)
    # replyform = ReplyCreateForm()
    
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid:
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post            
            comment.save()
            
    # context = {
    #     'post' : post,
    #     'comment': comment,
    #     # 'replyform': replyform
    # }

    return redirect('post', post.id)

def reply_sent(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    replyform = ReplyCreateForm()
    
    if request.method == 'POST':
        form = ReplyCreateForm(request.POST)
        if form.is_valid:
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent_comment = comment            
            reply.save()
            
    # context = {
    #     'reply' : reply,
    #     'comment': comment,
    #     'replyform': replyform
    # }
    return redirect('post', comment.parent_post.id)

def comment_delete_view(request, pk):
    post = get_object_or_404(Comment, id=pk, author=request.user)
    
    if request.method == "POST":
        post.delete()
        messages.success(request, 'Comment deleted')
        return redirect('post', post.parent_post.id )
        
    return render(request, 'aposts/comment_delete.html', {'comment' : post})

def like_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        
    return redirect('post', pk=post.id)