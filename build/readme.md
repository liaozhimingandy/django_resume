构建步骤

参考链接: [进阶指南：如何编写可重用程序 )](https://docs.djangoproject.com/zh-hans/5.0/intro/reusable-apps/)

1. 构建

   ```python
   python setup.py sdist
   ```

2. 校验

   ```
   # pip install twine
   twine check dist/*
   ```

3. 上传

   ```
   # C:\Users\liaoz目录下创建.pypirc文件,内容如下;
   [pypi]
     username=__token__
     password=pypi-AgEIcHlwaS5vcmcCJDY1NjVmZDVmLWEyZTUtNDg4MC1hNjIzLTU1M2Q1YjExNDk2NQACKlszLCI3ZTMxODYxZC0zMTM4LTRjYTYtOTg4ZC00OTQ3MTBiMDgzOGQiXQAABiBzNzka66EVB_FHgsAQzK2u07WI4AVuGIHrwBRQ7aYhuw
     
   python -m twine upload  dist/* --verbose
   ```

4. 本地安装

   ```
    python -m pip install --user django-resumes-1.0.2.tar.gz
   ```