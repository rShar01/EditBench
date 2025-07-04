from beem.discussions import Discussions, Query
from beem.comment import Comment
import random
import string

n_respuestas_minimas = 5
diccionario = {}

def procesar(texto: str):
    return "count me " in texto

def is_own_author(autor: str):
    return autor == '<masked_1>'

def is_banned(autor: str):
    list_banned = []
    return autor in list_banned

def generar_permlink_unico() -> str:
    return "".join(random.choices(string.digits, k=10))

def procesar_replies(replies: Comment):
    pass

def preparar_comentario(parent_author: str, parent_permlink: str, permlink: str, title: str = '', author: str = '<masked_1>', body: str = 'Count me in ^^ @<masked_1>') -> dict:
    return {
        "parent_author": parent_author,
        "parent_permlink": parent_permlink,
        "author": author,
        "permlink": permlink,
        "title": title,
        "body": body,
    }

q = Query()
d = Discussions()

# Modified highlighted section:
posts_generator = d.get_discussions("created", q, limit=6000)
X = 0

for post in posts_generator:
    post_author = post['author']
    post_permlink = post['permlink']
    num_replies = post['children']
    X += 1
    if num_replies > n_respuestas_minimas:
        comment = Comment(authorperm=f"{post_author}/{post_permlink}")
        replies_list = comment.get_replies()
        valid_replies = []
        cnt = 0
        for reply in replies_list:
            author = reply['author']
            text = reply['body']
            if is_own_author(author):
                # Reevaluar el comentario
                break
            if is_banned(author):
                break
            if procesar(text):
                cnt += 1
                valid_replies.append({
                    "author": reply['author'],
                    "permlink": reply['permlink'],
                    "body": reply['body']
                })
        if cnt > 3:
            diccionario[post_permlink] = {
                "post_author": post_author,
                "post_permlink": post_permlink,
                "replies": valid_replies
            }
            print("Iterador: ", X)
            print(valid_replies[-1]['author'], '/', valid_replies[-1]['permlink'])
