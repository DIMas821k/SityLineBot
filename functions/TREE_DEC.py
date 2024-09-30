import sqlite3
import pandas as pd

from config import  database_path

class Node:
    def __init__(self, node_id, name, is_leaf, visible=True, optional_datas=None):
        self.node_id = str(node_id)  # Всегда сохраняем идентификатор как строку
        self.name = name
        self.is_leaf = is_leaf
        self.parent = self
        self.children = []
        self.ancestors = []
        self.descendants = []
        self.description = None
        self.optional_datas = optional_datas if optional_datas else {}
        self.visible = visible
        self.information = ""

    def write_information(self):
        pass

    def add_child(self, child_node: any) -> None:
        """Добавляем дочерний узел и обновляем предков/потомков"""
        self.children.append(child_node)
        child_node.parent = self
        # Обновляем предков для child_node
        child_node.ancestors = self.ancestors + [self]
        # Обновляем потомков для текущего узла
        self.update_descendants(child_node)

    def update_descendants(self, node):
        """Обновляем всех потомков текущего узла, избегая зацикливания"""
        if node not in self.descendants:  # Проверяем, не добавлен ли уже потомок
            self.descendants.append(node)
        # Останавливаем рекурсию, если мы достигли корневого узла
        if self.parent and self.node_id != self.parent.node_id:
            self.parent.update_descendants(node)

    def display_tree(self, level=0):
        """Рекурсивно выводим дерево с отступами, если узел видим"""
        if not self.visible:  # Пропускаем невидимые узлы
            return

        indent = "    " * level  # Каждый уровень отступа увеличивается
        leaf_marker = " (Leaf)" if self.is_leaf else ""
        print(f"{indent}- {self.name}{leaf_marker}, {self.node_id}")

        for child in self.children:
            child.display_tree(level + 1)

    def get_ancestor(self) -> object:
        """Возвращаем ближайшего предка"""
        if self.ancestors:
            return self.ancestors[-1]  # Возвращаем самого ближнего предка (последний в списке)
        return None  # Если предков нет

    def print_options(self):
        print(self.optional_datas)

    def options(self):
        return self.optional_datas
    def get_optional_data(self, key):
        return self.optional_datas.get(key)
    def __repr__(self):
        return f"Node({self.node_id}, {self.name}, Leaf={self.is_leaf})"


class Tree:
    def __init__(self, db_path):
        self.db_path = db_path
        self.nodes = {}
        self.load_from_db()

    def get(self, node_id: object, options: object = None) -> Node:
        node_id = str(node_id)  # Приводим node_id к строке
        if node_id in self.nodes:
            return self.nodes[node_id]
        else:
            return None  # Если узел не найден

    def _add_additional_nodes(self, move_table, leaf_node_id):
        """Загружаем дополнительные узлы для листовых узлов из указанной таблицы"""
        leaf_node = self.get_node(leaf_node_id)

        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM {move_table} WHERE from_id = {leaf_node_id}"

        df = pd.read_sql_query(query, conn)
        conn.close()
        rows, columns = list(df.values), list(df.columns)

        for row in df.values:
            new_node_id = f"{leaf_node_id}_{len(leaf_node.children) + 1}"  # Идентификатор как строка
            optional_datas = dict(map(lambda i: (columns[i], row[i]), range(1, len(columns))))
            new_node = Node(new_node_id, optional_datas["название"], is_leaf=True, optional_datas=optional_datas)
            new_node.parent = leaf_node
            leaf_node.add_child(new_node)
            self.nodes[new_node_id] = new_node
        return

    def load_from_db(self):
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM actions"
        df = pd.read_sql_query(query, conn)
        rows, columns = list(df.values), list(df.columns)
        conn.close()
        # Создаём узлы
        for row in rows:
            node_id = str(row[0])  # Приводим идентификатор к строке
            parent_id = str(row[2]) if row[2] is not None else None  # Приводим идентификатор родителя к строке
            optional_datas = (dict(map(lambda i: (columns[i], row[i]), range(4, len(columns)))))
            new_node = Node(node_id, row[1], bool(row[3]), visible=optional_datas["visible"],
                            optional_datas=optional_datas)
            self.nodes[node_id] = new_node


        # Устанавливаем связи между узлами

        for row in rows:

            node_id = str(row[0])
            parent_id = str(row[2]) if row[2] is not None else None
            if parent_id and parent_id != node_id:
                parent_node = self.nodes[parent_id]
                child_node = self.nodes[node_id]
                parent_node.add_child(child_node)

                if row[3] and child_node.optional_datas.get("move_table"):

                    self._add_additional_nodes(child_node.optional_datas.get("move_table"), node_id)


    def display_tree(self, root_id=None):
        """Выводим дерево начиная с корня или указанного узла"""
        if root_id is None:
            root_node = next((node for node in self.nodes.values() if node.parent is None), None)
        else:
            root_node = self.get_node(str(root_id))  # Приводим root_id к строке

        if root_node:
            root_node.display_tree()
        else:
            pass

    def get_node(self, node_id: object) -> Node:
        return self.nodes.get(str(node_id), None)  # Приводим node_id к строке

    def get_parent_id(self, node_id: int) -> str:
        return self.get(str(node_id)).parent.node_id

    def get_children(self, node_id: int) -> list[Node]:
        return self.nodes.get(str(node_id), None).children if self.nodes.get(str(node_id), None) else []

    def get_children_ids(self, node_id):
        return [child.node_id for child in self.get_children(str(node_id))]

    def get_ancestors(self, node_id: int) -> Node:
        return self.get(str(node_id), None).parent if self.nodes.get(str(node_id), None) else None

    def get_ancestors_ids(self, node_id):
        return self.get_ancestors(str(node_id)).node_id

    def __repr__(self):
        return f"Tree with {len(self.nodes)} nodes"


Tree_Des = Tree(database_path)
