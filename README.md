# word2vec簡易版

主要是參考這篇文章：[我爱自然语言处理](http://www.52nlp.cn/%E4%B8%AD%E8%8B%B1%E6%96%87%E7%BB%B4%E5%9F%BA%E7%99%BE%E7%A7%91%E8%AF%AD%E6%96%99%E4%B8%8A%E7%9A%84word2vec%E5%AE%9E%E9%AA%8C)


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisities

* Ubuntu需要先安裝：

```
sudo pip install virtualenv
```

### Installing

1. 先下載專案： `git clone git@github.com:UDIC-lab-NCHU/word2vec.git`
2. 然後建議使用virtualenv： `virtualenv venv`
3. 啟動虛擬環境： `. venv/bin/activate`
4. 安裝所有需要的套件： `make install`

## Run

* `python querySoup.py {維基的model檔案} {你要查詢的單字}`

### Result

* 執行 `python querySoup.py wiki.zh.test.model 胸部` 的結果：

```
腹部 0.87651771307
背部 0.834844350815
頸部 0.814903199673
頭部 0.79481947422
臀部 0.788149833679
面部 0.768252432346
軀幹 0.753759682178
大腿 0.747038841248
腰部 0.745790183544
頭頂 0.742687821388
```

## Built With

* python2.7

## Versioning

For the versions available, see the [tags on this repository](https://github.com/Stufinite/Time-To-Dinner/releases).

## Contributors
* **張泰瑋** [david](https://github.com/david30907d)

## License

## Acknowledgments
