from operator import itemgetter


class Pagination:

    @classmethod
    def paginate_list(cls, items, page_size, page_index, sort_key=None, reverse=True):
        """
        对所有查询结果进行分页处理
        :param items:
        :param page_size: 每页多少个条目
        :param page_index: 当前查询哪一页
        :param sort_key: 用哪个key排序
        :param reverse: 是否倒序
        :return: (第page_index页的数据, 总条数)
        """
        # 先按时间倒序
        if sort_key:
            items = sorted(items, key=itemgetter(sort_key), reverse=reverse)

        total_count = len(items)

        if page_index == 0:
            page_index = 1
        page_index = page_index - 1

        if total_count <= page_size:
            # 不够一页，返回所有
            return items, total_count

        if page_size * page_index > total_count:
            # 超出最大数据
            return [], total_count

        idx_begin = page_index * page_size
        idx_end = idx_begin + page_size
        return items[idx_begin: idx_end], total_count


if __name__ == '__main__':
    _items = [
        dict(
            x=1, y=2, z=6
        ),
        dict(
            x=4, y=8, z=4
        ),
        dict(
            x=5, y=3, z=1
        ),
        dict(
            x=2, y=5, z=3
        ),
        dict(
            x=3, y=1, z=9
        ),
        dict(
            x=7, y=2, z=6
        ),
        dict(
            x=9, y=8, z=4
        ),
        dict(
            x=6, y=3, z=1
        ),
        dict(
            x=8, y=5, z=3
        ),
        dict(
            x=0, y=1, z=9
        ),
        dict(
            x=10, y=1, z=9
        ),
    ]
    _page_size = 3
    rst, count = Pagination.paginate_list(_items, _page_size, 0, sort_key='x')
    assert count == len(_items)
    assert _page_size == len(rst)
    assert rst[0]['x'] == 10
    assert rst[1]['x'] == 9
    assert rst[2]['x'] == 8
    rst, count = Pagination.paginate_list(_items, _page_size, 1, sort_key='x')
    assert count == len(_items)
    assert _page_size == len(rst)
    assert rst[0]['x'] == 10
    assert rst[1]['x'] == 9
    assert rst[2]['x'] == 8
    rst, count = Pagination.paginate_list(_items, _page_size, 2, sort_key='x')
    assert count == len(_items)
    assert _page_size == len(rst)
    assert rst[0]['x'] == 7
    assert rst[1]['x'] == 6
    assert rst[2]['x'] == 5
    rst, count = Pagination.paginate_list(_items, _page_size, 3, sort_key='x')
    assert count == len(_items)
    assert _page_size == len(rst)
    assert rst[0]['x'] == 4
    assert rst[1]['x'] == 3
    assert rst[2]['x'] == 2
    rst, count = Pagination.paginate_list(_items, _page_size, 4, sort_key='x')
    assert count == len(_items)
    assert 2 == len(rst)
    assert rst[0]['x'] == 1
    assert rst[1]['x'] == 0
