from beem.discussions import Discussions, Query
from beem.comment import Comment
import random
import string

n_respuestas_minimas = 5
diccionario = []  # Ahora usamos una lista de diccionarios para la jerarquía

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

def preparar_comentario(parent_author: str, parent_permlink: str, permlink: str, title: str = '', author: str = '<masked_1>', body: str = 'Count me in ^^ @<masked_1>') -> dict[str, str]:
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
posts_generator = d.get_discussions("created", q, limit=6000)
X = 0

for post in posts_generator:
    post_author = post['author']
    post_permlink = post['permlink']
    post_replies_count = post['children']
    X += 1
    hierarchical_replies = []  # Lista para almacenar los replies que cumplan la condición

    if post_replies_count > n_respuestas_minimas:
        comment = Comment(authorperm=f"{post_author}/{post_permlink}")
        post_replies = comment.get_replies()  # Obtenemos la lista de replies
        
        for reply in post_replies:
            author = reply['author']
            text = reply['body']
            if is_own_author(author):
                # Si se encuentra un reply del mismo autor, se descarta este post
                hierarchical_replies = []
                break
            if is_banned(author):
                # Si el autor está baneado, se descarta este post
                hierarchical_replies = []
                break
            if procesar(text):
                # Agregamos el reply que cumple la condición
                hierarchical_replies.append({
                    "author": reply['author'],
                    "permlink": reply['permlink'],
                    "body": reply['body']
                })
    
    if len(hierarchical_replies) > 3:
        # Se añade al diccionario jerárquico un item con la clave del post y la lista de sus replies
        diccionario.append({f"{post_author}/{post_permlink}": hierarchical_replies})

# Puedes hacer algo con "diccionario", por ejemplo, imprimirlo
print(diccionario)
