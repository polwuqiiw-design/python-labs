# Построение бинарного дерева

**Выполнила:** Полторацкая Анастасия, 2об_ПОО

## Задание

Необходимо реализовать нерекурсивную функцию `gen_bin_tree`, которая строит бинарное дерево.

Мои параметры:

- `root = 10`
- `height = 5`
- левый потомок: `root * 3 + 1`
- правый потомок: `3 * root - 1`

## Решение

Дерево хранится в виде словаря. Для построения используется цикл, поэтому функция является нерекурсивной.

```python
"""Построение бинарного дерева нерекурсивным способом."""


def gen_bin_tree(height: int = 5, root: int = 10) -> dict:
    """Создает бинарное дерево заданной высоты.

    Args:
        height: Высота дерева.
        root: Значение корня дерева.

    Returns:
        Построенное бинарное дерево в виде словаря.
    """
    tree = {
        "value": root,
        "left": None,
        "right": None
    }

    current_level = [tree]

    for level in range(1, height):
        next_level = []

        for node in current_level:
            value = node["value"]

            left_value = value * 3 + 1
            right_value = 3 * value - 1

            left_node = {
                "value": left_value,
                "left": None,
                "right": None
            }

            right_node = {
                "value": right_value,
                "left": None,
                "right": None
            }

            node["left"] = left_node
            node["right"] = right_node

            next_level.append(left_node)
            next_level.append(right_node)

        current_level = next_level

    return tree


tree = gen_bin_tree()
print(tree)
```

## Вывод

В ходе работы была реализована функция построения бинарного дерева без использования рекурсии. Для хранения дерева использовался словарь.
