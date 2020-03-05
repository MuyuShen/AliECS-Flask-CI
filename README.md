# AliECS-Flask-CI
pre-project for flask-ci-demo project

# Why this project?
本项目是用于理解和使用ECS部署的项目。
我之前一直使用本地环境进行web开发，但由于celery和其他组件对于windows系统的有限支持，只能使用本地虚拟化环境。
本地虚拟化环境在新机器上部署的时候特别缓慢，尤其是受限于网络速度。因而考虑使用云服务器来部署开发环境。
为了保证开发环境的拓展和快速部署，项目所有内容都运行在docker中。在使用组件化的构建之前，打算先从容器构建和通信开始。
