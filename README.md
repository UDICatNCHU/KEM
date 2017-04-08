# KEM
## Get Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisities

Ubuntu需要先安裝：

```bash
sudo pip install virtualenv
```

## Installing

1. 先下載專案： `git clone https://github.com/UDICatNCHU/KEM.git`
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

#### 執行 `python kem.py 草履蟲 100` 的結果(部分)：

```bash
['原生動物', 0.7895185351371765]
['藍菌', 0.7865398526191711]
['甲藻', 0.7792112827301025]
['藍綠藻', 0.7636655569076538]
['芽孢', 0.7631546258926392]
['兼性', 0.7622398138046265]
['纖毛蟲', 0.7605307102203369]
['專性', 0.7589520215988159]
['莢膜', 0.7575902938842773]
['蟲類', 0.7529693841934204]
['菌門', 0.7505052089691162]
['厚壁', 0.75014328956604]
['厭氧菌', 0.7490075826644897]
['桿菌屬', 0.7489725947380066]
['變形蟲', 0.748399555683136]
['介殼', 0.7460906505584717]
['節肢動物', 0.7445138692855835]
['纖毛', 0.744355320930481]
['革蘭氏', 0.7432918548583984]
['黴菌', 0.7408658266067505]
...
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
