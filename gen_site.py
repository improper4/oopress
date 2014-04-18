#!/usr/bin/python
#-*- encoding:utf-8 -*-
'''
Created on Apr 14, 2014
@author: sunlt

static_dir中的内容会被复制到site_static_dir中。
img_dir中的内容会被复制到site_img_dir中。
/page/2用来访问文章列表的第2分页
/关于.html是真正的page。
'''

import jinja2
import os
import shutil
import codecs
import markdown
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

CONFIG = {
          'app_path': '.',
          'posts_dir': '/_posts',
          'pages_dir': '/_pages',
          'static_dir': '/_static',
          'img_dir': '/_images',
          'extra_dir': '/_extras',
          'layout_dir': '/_layouts',
          'site_dir': '/_site',
          'site_static_dir': '/static', #./_site/static
          'site_page_dir': '',    #./_site
          'site_post_dir': '/post', #./_site/post
          'site_img_dir':'/images',   #./_site/imgages
          'site_tag_dir':'/tag',
          'site_category_dir':'/category',
          'site_url':'http://blog.letiantian.me',
          'site_title':'oopress～',
          'site_subtitle':'一个静态博客生成系统'
          }

def getTemplate(config, template_file):
    '''
    config: 保存配置项的字典 
    '''
    print '>>> getTemplate()'
    print '\ttemplate file: ',template_file
    templateLoader = jinja2.FileSystemLoader( searchpath = config['app_path'] + config['layout_dir'] )
    templateEnv = jinja2.Environment( loader=templateLoader )
    return templateEnv.get_template( template_file )

def cleanSite(config):
    '''
    清空CONFIG[site_dir']，重建目录
    '''
    def try_mkdir(dir_name):
        ''' '''
        try:
            os.mkdir(dir_name)
        except:
            pass
            
    shutil.rmtree(config['app_path'] + config['site_dir'])
    os.makedirs(config['app_path'] + config['site_dir'])
    try_mkdir(config['app_path'] + config['site_dir'] + config['site_page_dir'])
    try_mkdir(config['app_path'] + config['site_dir'] + config['site_post_dir'])
    try_mkdir(config['app_path'] + config['site_dir'] + config['site_tag_dir'])
    try_mkdir(config['app_path'] + config['site_dir'] + config['site_category_dir'])
    #try_mkdir(config['app_path'] + config['site_dir'] + config['site_post_list_dir'])
    
    shutil.copytree(config['app_path'] + config['static_dir'], config['app_path'] + config['site_dir'] + config['site_static_dir'])
    shutil.copytree(config['app_path'] + config['img_dir'], config['app_path'] + config['site_dir'] + config['site_img_dir'])
    
    
def genStaticHTML(targetDir, file_name, file_content):
    ''' '''
    if not os.path.isdir(targetDir):
        os.makedirs(targetDir)
    with codecs.open(targetDir+'/'+file_name, 'w', encoding='utf-8') as f:
        f.write(file_content)
        

def getPostList(config):
    ''' 
    获取post列表，每个元素是post的路径 
    例如，返回：['/home/sunlt/Code/eclipse-python/pyJekyll/_posts/\xe5\x93\x88\xe5\x93\x88.md']
    '''
    file_path = []
    for root, dirs, files in os.walk(config['app_path'] + config['posts_dir']):
        if len(files) > 0:
            for f_name in files:
                file_path.append(root + '/' + f_name)
    return file_path
     
def getPageList(config):
    ''' 获取page列表，每个元素是page的路径 '''
    file_path = []
    for root, dirs, files in os.walk(config['app_path'] + config['pages_dir']):
        if len(files) > 0:
            for f_name in files:
                file_path.append(root + '/' + f_name)
    return file_path

def md2html(str_md):
    '''
    将markdown语法的str转换为html的str
    '''
    return markdown.markdown(str_md, extensions=['markdown.extensions.tables'])



def title2fileName(title):
    ''' hadoop streaming -> hadoop-streaming'''
    return title.replace(' ','-')

def getBaseInfoOfPosts(config, post_list):
    '''  
    post文件示例
    ---
    title:关于樂天笔记
    layout:page
    create_time:2014-04-07 18:00
    author:樂天
    cat:云计算
    tag:java,hadoop
    ---
    '''
    def noLowwerButStrip(s):
        return s.strip()
    
    print '>>> getBaseInfoOfPosts()'
    for pl in post_list:
        print '\t file:', pl
    infos = {}
    for f_path in post_list:
        print '\t', f_path
        count = 0
        for line in codecs.open(f_path, 'r', encoding='utf-8'):
            print '\t>',line
            if line.strip() == '---':
                if count == 1:
                    print 'break'
                    break
                if count == 0:
                    count += 1
                    print 'continue'
                    continue
            ls = line.split(':', 1)
            if ls[0].strip() == 'title': 
                title = ls[1].strip()
                print '\ttitle:',title
            elif ls[0].strip() == 'layout': 
                layout = ls[1].strip()
                print '\tlayout',layout
            elif ls[0].strip() == 'author': 
                author = ls[1].strip()
                print '\tauthor',author
            elif ls[0].strip() == 'time':
                create_date = ls[1].strip().split()[0].strip()
                create_time = ls[1].strip().split()[1].strip()
                print '\tcreate_date',create_date
                print '\tcreate_time',create_time
            elif ls[0].strip() == 'cat': 
                if len(ls[1].strip()) == 0:
                    cat = []
                elif ',' not in ls[1].strip():
                    cat = [ls[1].strip()]
                else:
                    cat = map(noLowwerButStrip, ls[1].split(','))
                print '\tcat',cat
            elif ls[0].strip() == 'tag': 
                if len(ls[1].strip()) == 0:
                    tag = []
                elif ',' not in ls[1].strip():
                    tag = [ls[1].strip()]
                else:
                    tag = map(noLowwerButStrip, ls[1].split(','))
                print '\ttag', tag
        local_from_path = f_path
        local_to_dir = config['app_path'] + config['site_dir'] + config['site_post_dir'] + '/' + create_date.replace('-','/')
        url =  config['site_post_dir'] + '/' + create_date.replace('-','/') + '/' + title2fileName(title) + '.html'
        
        infos.setdefault((create_date, create_time, title),{})
        infos[(create_date, create_time, title)]['layout'] = layout
        infos[(create_date, create_time, title)]['author'] = author
        infos[(create_date, create_time, title)]['cat'] = cat
        infos[(create_date, create_time, title)]['tag'] = tag
        infos[(create_date, create_time, title)]['local_from_path'] = local_from_path
        infos[(create_date, create_time, title)]['local_to_dir'] = local_to_dir
        infos[(create_date, create_time, title)]['url'] = url
        infos[(create_date, create_time, title)]['create_date'] = create_date
        infos[(create_date, create_time, title)]['create_time'] = create_time
        infos[(create_date, create_time, title)]['title'] = title
    return infos

def getBaseInfoOfPages(config, page_list):
    '''  
    post文件示例
    ---
    title:关于樂天笔记
    layout:page
    create_time:2014-04-07 18:00
    ---
    '''

    print '>>> getBaseInfoOfPosts()'
    for pl in page_list:
        print '\t file:', pl
    infos = {}
    for f_path in page_list:
        print '\t', f_path
        count = 0
        for line in codecs.open(f_path, 'r', encoding='utf-8'):
            print '\t>',line
            if line.strip() == '---':
                if count == 1:
                    print 'break'
                    break
                if count == 0:
                    count += 1
                    print 'continue'
                    continue
            ls = line.split(':', 1)
            if ls[0].strip() == 'title': 
                title = ls[1].strip() #不做大写变小写的处理
                print '\ttitle:',title
            elif ls[0].strip() == 'layout': 
                layout = ls[1].strip()
                print '\tlayout',layout
            elif ls[0].strip() == 'time':
                create_date = ls[1].strip().split()[0].strip()
                create_time = ls[1].strip().split()[1].strip()
                print '\tcreate_date',create_date
                print '\tcreate_time',create_time
        local_from_path = f_path
        local_to_dir = config['app_path'] + config['site_dir']
        url = '/' + title +'.html'
        
        infos.setdefault((create_date, create_time, title),{})
        infos[(create_date, create_time, title)]['layout'] = layout
        infos[(create_date, create_time, title)]['local_from_path'] = local_from_path
        infos[(create_date, create_time, title)]['local_to_dir'] = local_to_dir
        infos[(create_date, create_time, title)]['url'] = url
        infos[(create_date, create_time, title)]['create_date'] = create_date
        infos[(create_date, create_time, title)]['create_time'] = create_time
        infos[(create_date, create_time, title)]['title'] = title
    return infos

def genSortedInfoOfPages(config, pageInfos):
    ''' '''
    ''' 对postInfos进行排序 '''
    sorted_pageInfos = sorted(pageInfos.items())[::-1]

    return sorted_pageInfos

def getMDContent(local_path):
    ''' 从文件local_path中提取出markdown的内容 '''
    content = ''
    count = 0
    for line in codecs.open(local_path, 'r', encoding='utf-8'):
        if line.strip() == '---' or count < 2:
            if line.strip() == '---':
                count += 1
        else:
            content = content + line
    return content
        
        
    
def genPosts(config, postInfos, catInfos ,  tagInfos ,recentPostInfos, sortedPageInfos):
    '''
    postInfos是getBaseInfoOfPosts(config, post_list)的返回值。
    '''
    print '>>> genPosts'
    for post in postInfos:
        print post
        template = getTemplate(config, postInfos[post]['layout']+'.html')
        print '\tget content from ', postInfos[post]['local_from_path']
        post_md_content = getMDContent(postInfos[post]['local_from_path'])
        #print post_md_content
        #TODO:import
        post_html_content = template.render(post_content = md2html(post_md_content), 
                                            post_info=postInfos[post], 
                                            recent_post_infos = recentPostInfos,
                                            config = config, 
                                            tag_infos = tagInfos, 
                                            cat_infos = catInfos,
                                            sorted_page_infos = sortedPageInfos)
        #print '\tpost: ', post_html_content
        print 'write to: ',postInfos[post]['local_to_dir']+'/'+title2fileName(postInfos[post]['title'])+'.html'
        genStaticHTML(postInfos[post]['local_to_dir'], title2fileName(postInfos[post]['title']+'.html'), post_html_content)

def genPages(config, pageInfos, catInfos ,  tagInfos ,recentPostInfos , sortedPageInfos):
    '''
    pageInfos是getBaseInfoOfPages(config, page_list)的返回值
    '''
    print '>>> genPages'
    for page in pageInfos:
        print page
        template = getTemplate(config, pageInfos[page]['layout']+'.html')
        print '\tget content from ', pageInfos[page]['local_from_path']
        page_md_content = getMDContent(pageInfos[page]['local_from_path'])
        #print page_md_content
        #TODO:import
        page_html_content = template.render(page_content = md2html(page_md_content), 
                                            page_info=pageInfos[page],
                                            tag_infos = tagInfos,
                                            config = config,
                                            cat_infos = catInfos,
                                            recent_post_infos = recentPostInfos,
                                            sorted_page_infos = sortedPageInfos)
        #print '\tpost: ', page_html_content
        print 'write to: ',pageInfos[page]['local_to_dir']+'/'+pageInfos[page]['title']+'.html'
        genStaticHTML(pageInfos[page]['local_to_dir'], pageInfos[page]['title']+'.html', page_html_content)

def genSortedInfoOfPosts(config, postInfos):
    ''' 对postInfos进行排序 '''
    timePost = {}
    for pi in postInfos:
        # pi -> (u'2014-04-07', u'18:00', u'title-1')
        year_month = '-'.join(pi[0].split('-')[:2])
        print '\t year_month: ',year_month
        timePost.setdefault(year_month,{})  
        timePost[year_month].setdefault(pi,{})
        timePost[year_month][pi] = postInfos[pi]
        
    for tp in timePost:
        timePost[tp] = sorted(timePost[tp].items())[::-1]
        
    sorted_timePost = sorted(timePost.items())
    sorted_timePost = sorted_timePost[::-1]
    print '\tsorted_timePost:'
    
    for si in sorted_timePost:  ##新文章排在前面
        print '\t\t', si
    ##sorted_timePost=
    #[
    #(u'2014-04', [((u'2014-04-07', u'18:00', u'\u4eceHadoop streaming\u5230mrjob'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/2013/\xe4\xbb\x8eHadoop Streaming\xe5\x88\xb0mrjob.md', 'layout': u'post', 'title': u'\u4eceHadoop streaming\u5230mrjob', 'url': u'http://127.0.0.1/post/2014/04/07/\u4eceHadoop-streaming\u5230mrjob.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'18:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2014-04-07', u'18:00', u'title-1'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/2013/title-1.md', 'layout': u'post', 'title': u'title-1', 'url': u'http://127.0.0.1/post/2014/04/07/title-1.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'18:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2014-04-07', u'17:00', u'\u54c8\u54c8'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/\xe5\x93\x88\xe5\x93\x88.md', 'layout': u'post', 'title': u'\u54c8\u54c8', 'url': u'http://127.0.0.1/post/2014/04/07/\u54c8\u54c8.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'17:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'})])
    #(u'2013-04', [((u'2013-04-07', u'17:00', u'22'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/22.md', 'layout': u'post', 'title': u'22', 'url': u'http://127.0.0.1/post/2013/04/07/22.html', 'cat': [u'\u7f16\u7a0b'], 'tag': [u'java', u'hadoop'], 'create_time': u'17:00', 'create_date': u'2013-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2013/04/07'})])
    #]
    ##
    return sorted_timePost

def genSortedCatPost(config,  postInfos):
    ''' 
    '''
    catPost = {}
    for pi in postInfos:
        cats = postInfos[pi]['cat']
        for cat in cats:
            catPost.setdefault(cat,{})
            catPost[cat].setdefault(pi,{})
            catPost[cat][pi] = postInfos[pi]

    for cp in catPost:
        print '\t', cp, catPost[cp]
    for cp in catPost:
        catPost[cp] = sorted(catPost[cp].items())[::-1]
    for cp in catPost:
        print '\t',cp, catPost[cp]

    sorted_catPost = sorted(catPost.items())
    sorted_catPost = sorted_catPost[::-1]
    print '\tsorted_catPost:'
    for si in sorted_catPost:  ##新文章排在前面
        print '\t\t', si
      
    ##[    
    #(u'\u7f16\u7a0b', [((u'2013-04-07', u'17:00', u'22'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/22.md', 'layout': u'post', 'title': u'22', 'url': u'http://127.0.0.1/post/2013/04/07/22.html', 'cat': [u'\u7f16\u7a0b'], 'tag': [u'java', u'hadoop'], 'create_time': u'17:00', 'create_date': u'2013-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2013/04/07'})])
    #(u'\u4e91\u8ba1\u7b97', [((u'2014-04-07', u'18:00', u'\u4eceHadoop streaming\u5230mrjob'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/2013/\xe4\xbb\x8eHadoop Streaming\xe5\x88\xb0mrjob.md', 'layout': u'post', 'title': u'\u4eceHadoop streaming\u5230mrjob', 'url': u'http://127.0.0.1/post/2014/04/07/\u4eceHadoop-streaming\u5230mrjob.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'18:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2014-04-07', u'18:00', u'title-1'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/2013/title-1.md', 'layout': u'post', 'title': u'title-1', 'url': u'http://127.0.0.1/post/2014/04/07/title-1.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'18:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2014-04-07', u'17:00', u'\u54c8\u54c8'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/\xe5\x93\x88\xe5\x93\x88.md', 'layout': u'post', 'title': u'\u54c8\u54c8', 'url': u'http://127.0.0.1/post/2014/04/07/\u54c8\u54c8.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'17:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'})])
    #]
    return sorted_catPost

def getAbstractOfPost(post_path):
    '''
    '''
    post_md_content = getMDContent(post_path)
    if "<!--more-->" in post_md_content:
        md_abstract = post_md_content.split("<!--more-->",1)[0]
        return md_abstract
    return post_md_content

def genSortedTagPost(config, postInfos):
    '''
    '''
    tagPost = {}
    for pi in postInfos:
        tags = postInfos[pi]['tag']
        for tag in tags:
            tagPost.setdefault(tag,{})
            tagPost[tag].setdefault(pi,{})
            tagPost[tag][pi] = postInfos[pi]

    for tp in tagPost:
        print '\t', tp, tagPost[tp]
    for tp in tagPost:
        tagPost[tp] = sorted(tagPost[tp].items())[::-1]
    for tp in tagPost:
        print '\t', tp, tagPost[tp]

    sorted_tagPost = sorted(tagPost.items())
    sorted_tagPost = sorted_tagPost[::-1]
    print '\tsorted_timePost:'
    for si in sorted_tagPost:  ##新文章排在前面
        print '\t\t', si
    
    ##[
    #(u'java', [((u'2014-04-07', u'18:00', u'\u4eceHadoop streaming\u5230mrjob'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/2013/\xe4\xbb\x8eHadoop Streaming\xe5\x88\xb0mrjob.md', 'layout': u'post', 'title': u'\u4eceHadoop streaming\u5230mrjob', 'url': u'http://127.0.0.1/post/2014/04/07/\u4eceHadoop-streaming\u5230mrjob.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'18:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2014-04-07', u'18:00', u'title-1'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/2013/title-1.md', 'layout': u'post', 'title': u'title-1', 'url': u'http://127.0.0.1/post/2014/04/07/title-1.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'18:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2014-04-07', u'17:00', u'\u54c8\u54c8'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/\xe5\x93\x88\xe5\x93\x88.md', 'layout': u'post', 'title': u'\u54c8\u54c8', 'url': u'http://127.0.0.1/post/2014/04/07/\u54c8\u54c8.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'17:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2013-04-07', u'17:00', u'22'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/22.md', 'layout': u'post', 'title': u'22', 'url': u'http://127.0.0.1/post/2013/04/07/22.html', 'cat': [u'\u7f16\u7a0b'], 'tag': [u'java', u'hadoop'], 'create_time': u'17:00', 'create_date': u'2013-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2013/04/07'})])
    #(u'hadoop', [((u'2014-04-07', u'18:00', u'\u4eceHadoop streaming\u5230mrjob'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/2013/\xe4\xbb\x8eHadoop Streaming\xe5\x88\xb0mrjob.md', 'layout': u'post', 'title': u'\u4eceHadoop streaming\u5230mrjob', 'url': u'http://127.0.0.1/post/2014/04/07/\u4eceHadoop-streaming\u5230mrjob.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'18:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2014-04-07', u'18:00', u'title-1'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/2013/title-1.md', 'layout': u'post', 'title': u'title-1', 'url': u'http://127.0.0.1/post/2014/04/07/title-1.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'18:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2014-04-07', u'17:00', u'\u54c8\u54c8'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/\xe5\x93\x88\xe5\x93\x88.md', 'layout': u'post', 'title': u'\u54c8\u54c8', 'url': u'http://127.0.0.1/post/2014/04/07/\u54c8\u54c8.html', 'cat': [u'\u4e91\u8ba1\u7b97'], 'tag': [u'java', u'hadoop'], 'create_time': u'17:00', 'create_date': u'2014-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2014/04/07'}), ((u'2013-04-07', u'17:00', u'22'), {'local_from_path': '/home/sunlt/Code/eclipse-python/pyJekyll/_posts/22.md', 'layout': u'post', 'title': u'22', 'url': u'http://127.0.0.1/post/2013/04/07/22.html', 'cat': [u'\u7f16\u7a0b'], 'tag': [u'java', u'hadoop'], 'create_time': u'17:00', 'create_date': u'2013-04-07', 'local_to_dir': u'/home/sunlt/Code/eclipse-python/pyJekyll/_site/post/2013/04/07'})])
    #]
    return sorted_tagPost

def getRecentPost(config, postInfos, post_top_num):
    ''' '''
    count = 0
    result = []
    infos = {}
    for pi in postInfos:
        infos[pi] = postInfos[pi].copy()
        infos[pi]['abstract'] = md2html(getAbstractOfPost(infos[pi]['local_from_path']))
    
    sorted_infos = sorted(infos.items())
    print '\tsorted_infos:'
    for si in sorted_infos[::-1]:  ##新文章排在前面
        print '\t\t', si
    sorted_infos = sorted_infos[::-1]
    
    for si in sorted_infos:
        count += 1
        if count >= post_top_num:
            break
        result.append(si)
    return result


def genIndexOfSite(config, recentPostInfos, catInfos, tagInfos, layout, sortedPageInfos):
    '''
    生成site的首页
    '''
    print '>>>', 'genIndexOfSite'
    template = getTemplate(config, layout)
    
    index_html_content = template.render(recent_post_infos = recentPostInfos, 
                                         config = config,
                                         cat_infos = catInfos,
                                         tag_infos = tagInfos,
                                         sorted_page_infos = sortedPageInfos)
    print config['app_path']+config['site_dir']+'/index.html'
    genStaticHTML(config['app_path']+config['site_dir'], 'index.html', index_html_content)
    

def genCatIndex(config, sortedCatPost, tagInfos, catInfos, layout, recentPostInfos, sortedPageInfos):
    '''_site/category/ '''
    template = getTemplate(config, layout)

    sorted_catPost = sortedCatPost

    cat_index_html_content = template.render(config = config,
                                             cat_posts = sorted_catPost,
                                             cat_infos = catInfos,
                                             tag_infos = tagInfos,
                                             recent_post_infos = recentPostInfos,
                                             sorted_page_infos = sortedPageInfos)
    
    print config['app_path']+config['site_category_dir'] + '/index.html'
    genStaticHTML(config['app_path']+config['site_dir']+config['site_category_dir'], 'index.html', cat_index_html_content)


    
    
def genTagIndex(config, sortedTagPost, tagInfos, catInfos, layout,recentPostInfos, sortedPageInfos):
    '''_site/tag/ '''
    template = getTemplate(config, layout)

    sorted_tagPost = sortedTagPost
        
    tag_index_html_content = template.render(config = config,
                                             tag_posts = sorted_tagPost,
                                             cat_infos = catInfos,
                                             tag_infos = tagInfos,
                                             recent_post_infos = recentPostInfos,
                                             sorted_page_infos = sortedPageInfos)
    
    print config['app_path']+config['site_tag_dir'] + '/index.html'
    genStaticHTML(config['app_path']+config['site_dir']+config['site_tag_dir'], 'index.html', tag_index_html_content)



def getTagInfos(config, sortedTagPost):
    ''' 
    'name':
    {
    'anchor': 'tag-1'
    'url'
    'post_num'
    'font_size':8pt
    }
    '''
    def get_font_size(post_num):
        if post_num < 5:
            return '14pt'
        elif post_num < 10:
            return '16pt'
        elif post_num < 15:
            return '17pt'
        elif post_num < 20:
            return '18pt'
        elif post_num < 25:
            return '20pt'
        else:
            return '22pt'
            
    tagInfos = {}
    for st in sortedTagPost:
        tagInfos.setdefault(st[0], {})
        tag_name_no_apace = title2fileName(st[0])
        tagInfos[st[0]]['anchor'] = tag_name_no_apace
        tagInfos[st[0]]['url'] =  config['site_tag_dir']+'/index.html#'+tag_name_no_apace
        tagInfos[st[0]]['post_num'] = len(st[1])
        tagInfos[st[0]]['font_size'] = get_font_size(len(st[1]))
    
    return tagInfos

def getCatInfos(config, sortedCatPost):
    '''
    {
    'name'
    'anchor': 'tag-1'
    'url'
    'post_num'
    'font-size':8pt
    }
    '''
    def get_font_size(post_num):
        if post_num < 5:
            return '14pt'
        elif post_num < 10:
            return '16pt'
        elif post_num < 15:
            return '17pt'
        elif post_num < 20:
            return '18pt'
        elif post_num < 25:
            return '20pt'
        else:
            return '22pt'
            
    catInfos = {}
    for sc in sortedCatPost:
        catInfos.setdefault(sc[0], {})
        cat_name_no_apace = title2fileName(sc[0])
        catInfos[sc[0]]['anchor'] = cat_name_no_apace
        catInfos[sc[0]]['url'] = config['site_category_dir']+'/index.html#'+cat_name_no_apace
        catInfos[sc[0]]['post_num'] = len(sc[1])
        catInfos[sc[0]]['font_size'] = get_font_size(len(sc[1]))
    return catInfos

def genPostIndex(config, sortedPostInfos, tagInfos, catInfos, layout, recentPostInfos, sortedPageInfos):
    ''' _site/post/index.html，按日期分类'''
    template = getTemplate(config, layout)

    post_index_html_content = template.render(config = config,
                                              time_posts = sortedPostInfos,
                                              tag_infos = tagInfos,
                                              cat_infos = catInfos,
                                              recent_post_infos = recentPostInfos,
                                              sorted_page_infos = sortedPageInfos)
    
    print config['app_path']+config['site_post_dir'] + '/index.html'
    genStaticHTML(config['app_path']+config['site_dir']+config['site_post_dir'], 'index.html', post_index_html_content)

def genErrorPage(config, sortedPostInfos, tagInfos, catInfos, layout, recentPostInfos, sortedPageInfos):
    '''
    生成_site/error.html
    '''
    template = getTemplate(config, layout)
    error_html_content =  template.render(config = config,
                                              time_posts = sortedPostInfos,
                                              tag_infos = tagInfos,
                                              cat_infos = catInfos,
                                              recent_post_infos = recentPostInfos,
                                              sorted_page_infos = sortedPageInfos )
    print config['app_path']+config['site_dir']+ '/error.html'
    genStaticHTML(config['app_path']+config['site_dir'], 'error.html', error_html_content)
    


def copyExtrasToSite(config):
    ''' '''
    from_dir = config['app_path'] + config['extra_dir']
    to_dir = config['app_path'] + config['site_dir']
    print 
    file_path = []
    for root, dirs, files in os.walk(from_dir):
        print root, dirs, files
        for f in files:
            print f
            shutil.copy(root+'/'+f, to_dir)
            
    
if __name__ == '__main__':

    cleanSite(CONFIG)
    
    page_infos = getBaseInfoOfPages(CONFIG, getPageList(CONFIG))
    sorted_pageInfos = genSortedInfoOfPages(config=CONFIG, pageInfos=page_infos)
    post_infos = getBaseInfoOfPosts(CONFIG, getPostList(CONFIG))
    recent_post_infos = getRecentPost(config=CONFIG, postInfos=post_infos, post_top_num=16)
    sorted_catPost = genSortedCatPost(CONFIG,  post_infos)
    sorted_tagPost = genSortedTagPost(CONFIG,  post_infos)
    sorted_postInfos = genSortedInfoOfPosts(config=CONFIG, postInfos=post_infos)
    cat_infos = getCatInfos(CONFIG, sorted_catPost)
    tag_infos = getTagInfos(CONFIG, sorted_tagPost)
    
    for pi in post_infos:
        print pi, post_infos[pi]
        
    genPosts(config = CONFIG, postInfos = post_infos, 
             catInfos = cat_infos, tagInfos = tag_infos, 
             recentPostInfos=recent_post_infos,
             sortedPageInfos=sorted_pageInfos)
    
    genPages(config = CONFIG, pageInfos = page_infos, 
             catInfos = cat_infos, tagInfos = tag_infos, 
             recentPostInfos=recent_post_infos,
             sortedPageInfos=sorted_pageInfos)

    genIndexOfSite(config=CONFIG, recentPostInfos=recent_post_infos, 
                   catInfos=cat_infos, tagInfos=tag_infos, layout='index.html',
                   sortedPageInfos=sorted_pageInfos)
    
    genPostIndex(config=CONFIG, sortedPostInfos=sorted_postInfos, 
                 tagInfos = tag_infos, catInfos = cat_infos, layout = 'post_index.html',
                 recentPostInfos=recent_post_infos,sortedPageInfos=sorted_pageInfos)
    genCatIndex(config=CONFIG, sortedCatPost = sorted_catPost, 
                tagInfos = tag_infos, catInfos = cat_infos, layout='cat_index.html',
                recentPostInfos=recent_post_infos,sortedPageInfos=sorted_pageInfos)
    genTagIndex(config=CONFIG, sortedTagPost = sorted_tagPost, 
                tagInfos = tag_infos, catInfos = cat_infos, layout = 'tag_index.html',
                recentPostInfos=recent_post_infos,sortedPageInfos=sorted_pageInfos)
    
    genErrorPage(config=CONFIG, sortedPostInfos=sorted_postInfos, tagInfos=tag_infos, 
                 catInfos=cat_infos, layout='error.html',  recentPostInfos=recent_post_infos,
                 sortedPageInfos=sorted_pageInfos)
    copyExtrasToSite(config=CONFIG)

