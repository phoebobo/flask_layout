# 这是七牛云的上传文件
from qiniu import Auth, put_data, put_file

bucket_name = 'apps'


def upload_file_qiniu(input_data):
    '''
    :param input_data: bytes类型文件
    :return: 返回上传的文件名
    '''
    q = Auth('LJ02GD-hS4BtGSxqeaF9Hk75o5yLl7PVgvDtn8gQ', 'eQIkKsacAVnJJU8TFQJgd93-hsO3x4psOfzqGyei')

    token = q.upload_token(bucket_name)
    ret1, ret2 = put_data(up_token=token, key=None, data=input_data)

    print(ret1)
    print(ret2)

    # 判断是否上传成功
    if ret2.status_code != 200:
        raise Exception('文件上传失败')
    return ret1.get('key')
