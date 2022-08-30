from distutils.core import setup
setup(
  name = 'nonebot_plugin_xiuxian',         # How you named your package folder (MyLib)
  packages = ['nonebot_plugin_xiuxian'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'xiuxian模拟器',   # Give a short description about your library
  author = 'PinkCat',                   # Type in your name
  author_email = '578043031@qq.com',      # Type in your E-Mail
  url = 'https://github.com/s52047qwas/nonebot_plugin_xiuxian',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/s52047qwas/nonebot_plugin_xiuxian.git',    # I explain this later on
  keywords = ['plugin', 'nonebot', 'xiuxian'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'collections',       # 可以加上版本号，如validators=1.5.1
          'sqlite3',
          'pathlib',
          'nonebot'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
