"""
字典对象，可以用属性的方式操作字典
"""


class DictObject(dict):

    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value


if __name__ == '__main__':
    x = DictObject(z=1, y=3)
    x.a = 3
    print(x)
    print(x.a)
