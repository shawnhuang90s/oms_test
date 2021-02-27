import pymysql
import configparser
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
from oms_test.settings import BASE_DIR


class Config:
    """
    读取 MySQL 配置文件信息
    [dbMysql]
    host=127.0.0.01
    port=3306
    user=root
    password=123456
    db_name=oms_test
    """
    def __init__(self, config_filename=None):
        self.file_path = f'{BASE_DIR}/oms_conf/{config_filename}'
        self.parsing_obj = configparser.ConfigParser()
        self.parsing_obj.read(self.file_path)

    def get_section_list(self):
        """读取配置文件中的 [] 里的对象名, 比如这里的 ['dbMysql']"""
        return self.parsing_obj.sections()

    def get_option_list(self, section):
        """获取指定的某个 [] 对象下面包含的内容, 比如这里的 ['dbMysql'] 下面的配置内容"""
        return self.parsing_obj.options(section)

    def get_content_dict(self, section):
        """获取每个字段对应的值并放进一个字典中"""
        ret = dict()
        for option in self.get_option_list(section):
            value = self.parsing_obj.get(section, option)
            ret[option] = int(value) if value.isdigit() else value
        return ret


class BasePyMySQLPool:

    def __init__(self, host, port, user, password, db_name):
        self.host = host
        self.port = port
        self.user = user
        # 注意密码要转化成字符串形式
        self.password = str(password)
        self.db_name = db_name


class PyMySQLPool(BasePyMySQLPool):
    """
    MySQL 数据库对象, 负责产生数据库连接
    此类中的连接采用连接池实现获取连接对象
    """
    __pool = None

    def __init__(self, config_filename, conf_name):
        """初始化时设置数据库构造函数, 从连接池中获取连接, 并生成操作游标"""
        conf_obj = Config(config_filename=config_filename)
        self.conf_dict = conf_obj.get_content_dict(section=conf_name)
        super(PyMySQLPool, self).__init__(**self.conf_dict)
        self.conn = self.get_conn()
        self.cursor = self.conn.cursor()

    def get_conn(self):
        """从连接池中获取连接"""
        if self.__pool is None:
            self.__pool = PooledDB(
                creator=pymysql,
                mincached=1,
                maxcached=20,
                host=self.host,
                port=self.port,
                user=self.user,
                passwd=self.password,
                db=self.db_name,
                use_unicode=False,
                charset='utf8',
                cursorclass=DictCursor
            )
        return self.__pool.connection()

    def execute_sql(self, sql, param=None):
        """
        执行 sql 语句, 获取查询数量
        :param sql: sql 查询语句
        :param param: 如果有查询条件, 只需传递条件列表值 (元组/列表)
        :return: 受影响的行数
        """
        if not param:
            count = self.cursor.execute(sql)
        else:
            count = self.cursor.execute(sql, param)
        return count

    def get_all(self, sql, param=None):
        """
        执行 sql 查询语句, 获取所有数据
        :param sql: sql 查询语句
        :param param: 如果有查询条件, 只需传递条件列表值 (元组/列表)
        :return: 查询结果为字典对象或布尔值
        """
        count = self.execute_sql(sql, param)
        if count > 0:
            ret = self.cursor.fetchall()
        else:
            ret = False
        return ret

    def get_one(self, sql, param=None):
        """
        执行 sql 查询语句, 获取第一条数据
        :param sql: sql 查询语句
        :param param: 如果有查询条件, 只需传递条件列表值 (元组/列表)
        :return: 查询结果为字典对象或布尔值
        """
        count = self.execute_sql(sql, param)
        if count > 0:
            ret = self.cursor.fetchone()
        else:
            ret = False
        return ret

    def get_many(self, sql, num, param=None):
        """
        执行 sql 查询语句, 获取 num 条数据
        :param sql: sql 查询语句
        :param num: 指定获取 num 条数据
        :param param: 如果有查询条件, 只需传递条件列表值 (元组/列表)
        :return: 查询结果为字典对象或布尔值
        """
        count = self.execute_sql(sql, param)
        if count > 0:
            ret = self.cursor.fetchmany(num)
        else:
            ret = False
        return ret

    def insert(self, sql, param=None):
        """
        向数据表插入一条记录
        :param sql: sql 插入语句
        :param param: 要插入的某条记录
        :return: 受影响的行数
        """
        return self.execute_sql(sql, param)

    def insert_many(self, sql, param):
        """
        向数据表插入多条记录
        :param sql: sql 插入语句
        :param param: 要更新的多条记录 (列表或元组)
        :return: 受影响的行数
        """
        count = self.cursor.executemany(sql, param)
        return count

    def update(self, sql, param=None):
        """
        更新数据表记录
        :param sql: sql 更新语句
        :param param: 要更新的值 (列表或元组)
        :return: 受影响的行数
        """
        return self.execute_sql(sql, param)

    def replace(self, sql, param=None):
        """
        插入更新数据表记录
        :param sql: sql 插入更新语句
        :param param: 要插入更新的值 (列表或元组)
        :return: 受影响的行数
        """
        return self.execute_sql(sql, param)

    def delete(self, sql, param=None):
        """
        删除数据表记录
        :param sql: sql 删除语句
        :param param: 要删除的记录 (列表或元组)
        :return: 受影响的行数
        """
        return self.execute_sql(sql, param)

    def begin(self):
        """开启事务"""
        self.conn.autocommit(0)

    def end(self, option='commit'):
        """结束事务"""
        if option == 'commit':
            self.conn.commit()
        else:
            self.conn.rollback()

    def dispose(self, is_end=1):
        """释放连接池资源"""
        if is_end == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    obj = Config('oms_db.cnf')
    section_list = obj.get_section_list()
    for section in section_list:
        options_list = obj.get_option_list(section)
        print(options_list)  # ['host', 'port', 'user', 'password', 'db_name']
        content_dict = obj.get_content_dict(section)
        print(content_dict)  # {'host': '127.0.0.01', 'port': 3306, 'user': 'root', 'password': 123456, 'db_name': 'oms_test'}


