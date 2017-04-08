# word2vec簡易版

主要是參考這篇文章：[以 gensim 訓練中文詞向量](http://zake7749.github.io/2016/08/28/word2vec-with-gensim/)


## Get Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisities

Ubuntu需要先安裝：

```bash
sudo pip install virtualenv
```

## Installing

1. 先下載專案： `git clone git@github.com:UDIC-lab-NCHU/word2vec.git`
2. 然後建議使用virtualenv： `virtualenv venv`
3. 啟動虛擬環境： `. venv/bin/activate`
4. 安裝所有需要的套件： `make install`

## Run
#### Building the model
1. Running build.py
```bash
python build.py 結巴自訂字典path 停用詞path 欲訓練model之維度
```

2. import build class from build.py
```python
obj = build(結巴自訂字典path, 停用詞path, 欲訓練model之維度)
obj.exec()
```

#### Usage of KEM class
1. Running `kem.py`
```bash
python kem.py QueryTerm TopK
```

2. import `KEM` class from `kem.py`
```python
obj = KEM(MongoDB uri, word2vec model path)
obj.getTerms(query term, Top k results to return)
```


## Result

#### 執行 `python kem.py 日本 100` 的結果(部分)：

```bash
['日本政府', 0.5378537178039551]
['沖繩', 0.5037938356399536]
['東京', 0.4662987291812897]
['韓國', 0.4528932571411133]
['關西地區', 0.4191458821296692]
['九州', 0.41825416684150696]
['國外', 0.4169955849647522]
['日本帝國', 0.41695576906204224]
['日語', 0.416387677192688]
['大阪', 0.41383248567581177]
['japan', 0.4134363532066345]
['琉球', 0.4105386734008789]
['名古屋', 0.41011762619018555]
['朝鮮半島', 0.40963518619537354]
['臺灣', 0.4059162437915802]
['日本海軍', 0.39949870109558105]
['歐美', 0.3992425799369812]
['長崎', 0.398493230342865]
['讀賣新聞', 0.39827239513397217]
['京都', 0.3962410092353821]
['本國', 0.39571788907051086]
['東洋', 0.395452082157135]
['福島', 0.39438480138778687]
['美日', 0.3910793960094452]
['朝日新聞', 0.3879473805427551]
['明治維新', 0.3871694803237915]
['日本海', 0.38702329993247986]
['琉球羣島', 0.38652580976486206]
['海外', 0.38425546884536743]
['中國', 0.3836453855037689]
['外國', 0.3830639719963074]
['神奈川', 0.38256970047950745]
['軍國主義', 0.3824044466018677]
['朝鮮人', 0.38182151317596436]
etc
```

## Built With

python3.4

## Versioning

For the versions available, see the [tags on this repository](https://github.com/Stufinite/Time-To-Dinner/releases).

## Contributors
* __張泰瑋__ [david](https://github.com/david30907d)
* __游哲軒__ [Shane Yu](https://github.com/theshaneyu)

## License

## Acknowledgments
