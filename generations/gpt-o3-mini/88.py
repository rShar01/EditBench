from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def cluster_data(features_transformed, cluster_column_dict, n_clusters=2, clustering_method='kmeans'):
    """
    Выполняет кластеризацию данных для различных наборов столбцов.

    Args:
        features_transformed (pandas.DataFrame): Преобразованный DataFrame с параметрами.
        cluster_column_dict (dict): Словарь, где ключ – имя столбца, в который будут записаны 
                                    метки кластера, а значение – кортеж или список имен столбцов,
                                    по которым производится кластеризация.
        n_clusters (int): Количество кластеров.
        clustering_method (str): Метод кластеризации ('kmeans').

    Returns:
        pandas.DataFrame: DataFrame с добавленными столбцами меток кластеров.
    """
    if features_transformed is None:
        print("Сначала выполните преобразование данных (этап 5).")
        return None

    # Создаем копию DataFrame, чтобы не изменять исходные данные
    data_with_clusters = features_transformed.copy()

    for cluster_column_name, columns in cluster_column_dict.items():
        print(f"Выполняется кластеризация для столбцов: {columns} с сохранением меток в '{cluster_column_name}'")
        features_subset = data_with_clusters[list(columns)].copy()

        if clustering_method == 'kmeans':
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = model.fit_predict(features_subset)
            
            # Оценка качества кластеризации (например, с помощью коэффициента силуэта)
            if len(np.unique(cluster_labels)) > 1:  # Проверка на случай, когда все точки отнесены к одному кластеру
                silhouette_avg = silhouette_score(features_subset, cluster_labels)
                print(f"Коэффициент силуэта для {n_clusters} кластеров на столбцах {columns}: {silhouette_avg:.4f}")
            else:
                print(f"Невозможно рассчитать коэффициент силуэта для {n_clusters} кластера на столбцах {columns} (все точки в одном кластере).")
        else:
            print("Неподдерживаемый метод кластеризации.")
            return None

        # Добавляем результаты кластеризации в новый столбец с именем, указанным в ключе
        data_with_clusters[cluster_column_name] = cluster_labels
        print(f"Кластеризация для столбцов {columns} выполнена. Метки кластеров добавлены в столбец '{cluster_column_name}'.")

    return data_with_clusters

# Выполнение кластеризации (после этапа 5 и до этапа 6)
if 'features_transformed' in locals() and features_transformed is not None:
    # Определяем наборы столбцов для кластеризации.
    # Ключи словаря задают имена новых столбцов, а значения – кортежи или списки с именами исходных столбцов.
    cluster_column_dict = {
        'Кластер1': ('столбец1', 'столбец2'),
        'Кластер2': ('столбец3',)
    }
    n_clusters = 3  # Количество кластеров (подберите оптимальное значение)
    features_transformed = cluster_data(features_transformed, cluster_column_dict, n_clusters)
    
    # Визуализация кластеров (пример для случая, когда есть 2 числовых признака)
    numerical_features = features_transformed.select_dtypes(include=np.number)
    if numerical_features.shape[1] >= 2:
        plt.figure(figsize=(8, 6))
        # Визуализируем кластеры для первого набора столбцов (например, 'Кластер1')
        plt.scatter(numerical_features.iloc[:, 0], numerical_features.iloc[:, 1], c=features_transformed['Кластер1'], cmap='viridis')
        plt.xlabel(numerical_features.columns[0])
        plt.ylabel(numerical_features.columns[1])
        plt.title('Результаты кластеризации для Кластер1')
        plt.colorbar(label='Номер кластера')
        plt.show()
    else:
        print("Недостаточно числовых признаков для визуализации кластеров на плоскости.")
else:
    print("Сначала выполните этап 5 (Преобразование данных).")
