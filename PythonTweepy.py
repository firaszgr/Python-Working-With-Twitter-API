#!/usr/bin/env python
# coding: utf-8

# In[1]:


# First, we create an application in Twitter (via Twitter Developer Portal) to make sure we can access tweets.
# After setting up our app, we can access Twitter API in Python. Let's import some necessary Python libraries !

import tweepy as tw
import pandas as pd


# In[2]:


# In order to access Twitter API, we will need some elements from the Twitter app we just created ! 
# Let's go back to our Twitter app page and get the 4 necessary keys : 
# consumer key, consumer seceret key, access token key and access token secret key

consumer_key= 'uTVdIHCaqVRgX8QA7maNrV28L'
consumer_secret= 'V43BVmfloFrtsocqRfYADTqfs9jxO6EvO0gt6wIDzY1JH0XdM7'
access_token= '1387518162-fhfpmLmGz7i6RW11XvZpMGSVWq2dt27o0jbXj3B'
access_token_secret= '1NSHW4uEHmLanecAG1Si66OfOu9xJ21LKAaZK0GdEnJoB'


# In[3]:


# After defining our keys in Python, we can access the twitter API :

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)


# In[4]:


# Twitter API allows us to access only recent tweets (one week). Now we can look for the recent tweets we need ! 
# Given the recent events in Afghanistan, we'd like to look for tweets that use #AghanistanWar hashtag !
# Let's begin by defining our search terms and start date as variables in Python

search_words = "#afghanistanwar"
date_since = "2021-08-15"


# In[5]:


# .Cursor method will allow us to have an object containing tweets including the hashtag #afghanistanwar
tweets = tw.Cursor(api.search,
              q=search_words,
              lang="en",
              since=date_since).items(5)
tweets


# In[6]:


# Obviously, it returned an object containing the collected data, and this object can be iterated ! 
# Items in the iterator contain attributes such as tweet text, sender, date, etc.

tweets = tw.Cursor(api.search,
              q=search_words,
              lang="en",
              since=date_since).items(10)

# Iterate and print tweets
for tweet in tweets:
    print(tweet.text)


# In[7]:


# We'd like to remove retweets (content shared and not created by someone) since they include  duplicate content

new_search = search_words + " -filter:retweets"
new_search


# In[8]:


tweets = tw.Cursor(api.search,
                       q=new_search,
                       lang="en",
                       since=date_since).items(5)

[tweet.text for tweet in tweets]


# In[9]:


# Twitter API allows us also to access the user name and location for each tweet. Let's try this with the 1000 more recent tweets

tweets = tw.Cursor(api.search, 
                           q=new_search,
                           lang="en",
                           since=date_since).items(1000)

users_info = [[tweet.user.screen_name, tweet.user.location,tweet.text] for tweet in tweets]
users_info [:5]


# In[10]:


tweet_text = pd.DataFrame(data=users_info, 
                    columns=['user', "location","text"])
tweet_text


# In[11]:


# As we've seen above, there is less than 1000 recent tweets
# Let's use dtale library to have a better view of our dataframe : 

import dtale
dtale.show(tweet_text)


# In[12]:


# Before the analysis, let's clean our data
# We would like to begin by removing url from the tweets texts
# Let's first define all_tweets variable, which contains Tweets texts

tweets = tw.Cursor(api.search, 
                           q=new_search,
                           lang="en",
                           since=date_since).items(1000)

all_tweets = [tweet.text for tweet in tweets]
all_tweets[:5]


# In[13]:


# We then create remove_url function, based on regex, which removes url part from tweets texts 

def remove_url(txt):
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())


# In[14]:


# Use re library for regex expressions

import re
all_tweets_no_urls = [remove_url(tweet) for tweet in all_tweets]
all_tweets_no_urls[:5]


# In[15]:


# To continue our analysis, we need to lowercase words in all tweets, in order to get accurate results for words frequencies

words_in_tweet = [tweet.lower().split() for tweet in all_tweets_no_urls]
words_in_tweet[:5]


# In[16]:


# Let's use itertools library to put all the words in one list, to simplify the analysis

import itertools
all_words_no_urls = list(itertools.chain(*words_in_tweet))


# In[17]:


# Let's use Collections library to get most common words and their occurences with "most_common" method

import collections

counts_no_urls = collections.Counter(all_words_no_urls)
counts_no_urls.most_common(20)


# In[18]:


# Transform it into a dataframe

clean_tweets_no_urls = pd.DataFrame(counts_no_urls.most_common(20),
                             columns=['words', 'count'])

clean_tweets_no_urls.head()


# In[19]:


dtale.show(clean_tweets_no_urls)


# In[20]:


# Let's work with nltk library in order to clean data from stopwords

import nltk
nltk.download('stopwords')


# In[21]:


from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))


# In[22]:


tweets_no_stop = [[word for word in tweet_words if not word in stop_words]
              for tweet_words in words_in_tweet]

tweets_no_stop[0]


# In[23]:


all_words_no_stop = list(itertools.chain(*tweets_no_stop))

counts_no_stop = collections.Counter(all_words_no_stop)

counts_no_stop.most_common(20)


# In[24]:


# Now, let's just remove collection words (terms we used to look for our tweets)

collection_words = ['afghanistan', 'war', 'afghanistanwar']
tweets_no_stop_no_collec = [[w for w in word if not w in collection_words]
                 for word in tweets_no_stop]
tweets_no_stop_no_collec[0]


# In[25]:


# Flatten list of words in clean tweets
all_words_no_stop_no_collec = list(itertools.chain(*tweets_no_stop_no_collec))

# Create counter of words in clean tweets
counts_no_stop_no_collec = collections.Counter(all_words_no_stop_no_collec)

counts_no_stop_no_collec.most_common(20)


# In[26]:


clean_tweets_final = pd.DataFrame(counts_no_stop_no_collec.most_common(15),
                             columns=['words', 'count'])
clean_tweets_final.head()


# In[64]:


# Let's create a representative chart with matplotlib

get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib as mtplt
import matplotlib.pyplot as plt 
import tkinter

fig, ax = plt.subplots(figsize=(8, 8))

# Plot horizontal bar graph

clean_tweets_final.sort_values(by='count').plot.barh(x='words',
                      y='count',
                      ax=ax,
                      color="lightgreen")

ax.set_title("Most Common Words Found in Tweets")

plt.show()


# In[29]:


# Let's now work on bigrams. 
# Let's create lists for bigrams in tweets

from nltk import bigrams

bigram_words = [list(bigrams(tweet)) for tweet in tweets_no_stop_no_collec]


# In[30]:


# Bigrams are the co-occuring words. Let's see a concrete example : bigrams for the first tweet :

bigram_words[0]


# In[31]:


# Flatten list of bigrams in clean tweets with itertools chain method again 
bigrams = list(itertools.chain(*bigram_words))

# Create counter of words for clean tweets bigrams
bigram_counts = collections.Counter(bigrams)

bigram_counts.most_common(20)


# In[32]:


# Transform it to a dataframe

bigram_df = pd.DataFrame(bigram_counts.most_common(20),
                             columns=['bigram', 'count'])

bigram_df


# In[33]:


dtale.show(bigram_df)


# In[36]:


import networkx as nx

# Create dictionary of bigrams and their counts
d = bigram_df.set_index('bigram').T.to_dict('records')

# Create network plot 
G = nx.Graph()

# Create connections between nodes

for k, v in d[0].items():
    G.add_edge(k[0], k[1], weight=(v * 10))

G.add_node("china", weight=100)


# In[83]:


fig, ax = plt.subplots(figsize=(15, 15))

pos = nx.spring_layout(G, k=2)

# Plot networks
nx.draw_networkx(G, pos,
                 font_size=12,
                 width=3,
                 edge_color='gray',
                 node_color='lightgreen',
                 with_labels = False,
                 ax=ax)

# Create offset labels
for key, value in pos.items():
    x, y = value[0]+.1, value[1]+.045
    ax.text(x, y,
            s=key,
            bbox=dict(facecolor='yellow', alpha=0.5),
            horizontalalignment='center', fontsize=10)
    
plt.show()

