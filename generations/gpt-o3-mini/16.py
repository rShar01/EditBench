def main():
    # Cargamos pass
    a = load_env_tx_sign_pass('wif_posting_key')

    # h = Hive(node="https://api.hive.blog")
    q = Query()
    d = Discussions()

    # Nombre de usuario a verificar
    usuario_a_verificar = "<masked_1>"

    # Definir expresión regular para encontrar etiquetas HTML
    html_tags_regex = re.compile(r"<[^>]+>")

    # Obtener la lista de publicaciones -> List[Class: Comment]
    posts_generator = d.get_discussions("created", q, limit=2000)

    # Contador de post publicados
    count_post_publicados = 0
    count_post_modificados = 0

    # Cargo la lista de autores con respuestas preconfiguradas
    autores_preconfig = author_preconfig()

    # ==================== Inicio de procesamiento en paralelo ====================
    # Convertimos el generador en una lista para poder iterar paralelamente
    posts_list = list(posts_generator)

    # Función que procesa un solo post
    def process_single_post(idx_post):
        idx, post = idx_post
        local_published = 0
        local_modified = 0
        if post["author"] == "<masked_2>":
            return (0, 0)
        if idx % 50 == 0:
            print(f"post.items.created: {post['created']}")
        print(idx + 1)
        """# Si el autor esta en la lista de baneados salta a la siguiente iteracion
        if author_in_banned_list(post["author"]):
            continue"""

        try:
            # Crear un objeto Comment para el post
            post_comment = Comment(
                # authorperm="cryptochroma/woo-token-giveaway-woo-4-ffc"#, blockchain_instance=h
                authorperm=f"{post['author']}/{post['permlink']}"  # , blockchain_instance=h
            )

            replies = post_comment.get_replies()

            # Contar respuestas filtradas que contienen la palabra "count"
            count_replies = [
                reply for reply in replies if "count me " in reply["body"].lower()
            ]
            print("Numero de respuestas del post 'count me': ", len(count_replies))

            # Verificar si al menos cuatro usuarios han comentado "count"
            unique_users = set(reply["author"] for reply in count_replies)
            if len(unique_users) < 3:
                return (0, 0)

            # Verificar si el usuario ha respondido
            usuario_respondio = False
            for ax in replies:
                if ax["author"].lower() == usuario_a_verificar:
                    comentario_publicado = ax["body"]
                    permlink_publicado = ax["permlink"]
                    usuario_respondio = True
                    break

            # preparamos comentario
            comment_author = "<masked_1)"
            comment_parent_author = post["author"]
            comment_parent_permlink = post["permlink"]
            comment_title = ""
            comment_body = "Count me in ^^ @<masked_1>"

            # Bloque: buscar palabras que mas se repitan
            replies_all_data = post_comment.get_replies(raw_data=True)
            # Filtrar respuestas que contienen etiquetas HTML
            filtered_replies = [
                reply["body"].lower()
                for reply in replies_all_data
                if not re.search(html_tags_regex, reply["body"])
            ]

            # Lista de respuesta filtrada sin etiquetas html
            list_replies_filtered = set(filtered_replies)

            all_sentences = [
                sentence
                for content in list_replies_filtered
                for sentence in extract_sentences(content)
            ]
            if len(all_sentences) > 1:
                # print("lista completa:",all_sentences)
                sentence_frequency = count_sentence_frequency(all_sentences)
                # print("contador repetidos:",sentence_frequency)
                most_common_sentence = find_most_common_sentence(sentence_frequency)
                # print("Palabra más repetida:", most_common_sentence)
                if most_common_sentence is not None:
                    comment_body = "Count me in ^^ @<masked_1>\n" + most_common_sentence

            if post["author"] in autores_preconfig:
                if post["author"] == "<masked_3>" and "#GivePeaceAChance" in post.body:
                    comment_body = "Count me in ^^ @<masked_1> #GivePeaceAChance"
                if post["author"] == "<masked_4>" and "guess a number between" in post.body:
                    numero_aleatorio = random.randint(1, 500)
                    comment_body = "Count me in ^^ @<masked_1> {}".format(numero_aleatorio)
                if (
                    post["author"] == "<masked_5>"
                    and "choose a number from 1 to 10 depending how much you like that card"
                    in post.body
                ):
                    comment_body = "Count me in ^^ @<masked_1>. Rating 7"
                if post["author"] == "<masked_6>" and "WAX adress" in post.body:
                    comment_body = "Count me in ^^ @<masked_1>. zzkfm.wam"
                if post["author"] == "<masked_7>" and "ecency" in post.body.lower():
                    comment_body = "Count me in ^^ @<masked_1>. Ecency"
                if (
                    post["author"] == "<masked_8>"
                    and "Your job is to guess the exact weight of this coin" in post.body
                ):
                    numero_aleatorio = round(random.uniform(6, 9), 2)
                    comment_body = "Count me in ^^ @<masked_1> {} g".format(numero_aleatorio)
                if post["author"] == "new.things" and "atx" in post.body.lower():
                    comment_body = "Count me in ^^ @<masked_1>. ATX"

            if usuario_respondio and comment_body == comentario_publicado:
                print(f"\n{usuario_a_verificar} ha respondido a este post.", idx + 1)
                return (0, 0)

            # Generar un permlink único
            comment_permlink = "".join(random.choices(string.digits, k=10))

            if usuario_respondio and comment_body != comentario_publicado:
                comment_permlink = permlink_publicado
                print(
                    "\nComentario Modificado.\nComentario original: ",
                    comentario_publicado,
                    "\nComentario modificado: ",
                    comment_body,
                )
                local_modified += 1

            # Crear una instancia de TransactionBuilder
            tx = TransactionBuilder(blockchain_instance=h)

            # Agregar la operación de comentario al TransactionBuilder
            tx.appendOps(
                BaseComment(
                    **{
                        "parent_author": comment_parent_author,
                        "parent_permlink": comment_parent_permlink,
                        "author": comment_author,
                        "permlink": comment_permlink,
                        "title": comment_title,
                        "body": comment_body,
                    }
                )
            )

            # Agregar la clave de posting
            # tx.appendWif(os.getenv("wif_posting_key"))
            tx.appendWif(a)
            # Firmar y transmitir la transacción
            signed_tx = tx.sign()
            broadcast_tx = tx.broadcast(trx_id=True)

            print("*" * 50)
            print("\nComentario creado exitosamente para el post:", post["title"])
            print("\n\nValor de 'body':", broadcast_tx["operations"][0][1]["body"])
            print("*" * 50)

            # Espera 3 segundos
            time.sleep(3)

            # Actualizamos el contador de post publicados
            local_published += 1

        except Exception as e:
            print(f"Error processing post {idx + 1}: {e}")
        return (local_published, local_modified)

    # Procesar posts en paralelo utilizando ThreadPoolExecutor
    import concurrent.futures
    total_published = 0
    total_modified = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_single_post, enumerate(posts_list)))
    for pub, mod in results:
        total_published += pub
        total_modified += mod

    count_post_publicados = total_published
    count_post_modificados = total_modified
    # ==================== Fin de procesamiento en paralelo ====================

    print("\nNumero de post publicados:", count_post_publicados)
    print("\nNumero de post modificados:", count_post_modificados)


if __name__ == "__main__":
    main()
