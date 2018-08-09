# KEM

AKA word2vec, but our [nlp suite](https://github.com/udicatnchu/udic-nlp-api) all starts with prefix "k"

so named it as KEM, keyword embedding model.

[reference](http://zake7749.github.io/2016/08/28/word2vec-with-gensim/)

## Install

* (Recommended): Use [docker-compose](https://github.com/udicatnchu/udic-nlp-api) to install


## Manually Install

If you want to integrate `kem` into your own django project, use manually install.

* `pip install kem`

### Config
Cause this is a django app

so need to finish these django setups.

1. settings.py：

  ```python
  INSTALLED_APPS = [
      'kem'
       ...
  ]
  ```
2. urls.py：  

  ```python
  import kem.urls
  urlpatterns += [
      url(r'^kem/', include(kem.urls))
  ]
  ```
3. `python3 manage.py buildkem --lang <lang, e.g., zh or en or th> --dimension <int: e.g., 400> --cpus <default=6> --ontology <default=False>`
    * ontology: experimantal feature, see [details](https://github.com/UDICatNCHU/kem#experimental-feature)
4. fire `python manage.py runserver` and go `127.0.0.1:8000/` to check whether the config is all ok.

## API
1. get similar word:_`/kem`_
  - keyword
  - num (default=10)
  - ontology (default=False)
    1. example：<http://udiclab.cs.nchu.edu.tw/kem?keyword=草履蟲&num=100&lang=zh>

    ```json
    ["原生動物", 0.7895185351371765]
    ["藍菌", 0.7865398526191711]
    ["甲藻", 0.7792112827301025]
    ["藍綠藻", 0.7636655569076538]
    ["芽孢", 0.7631546258926392]
    ["兼性", 0.7622398138046265]
    ["纖毛蟲", 0.7605307102203369]
    ["專性", 0.7589520215988159]
    ["莢膜", 0.7575902938842773]
    ...
    etc
    ```
    2. example：<http://udiclab.cs.nchu.edu.tw/kem?keyword=中華民國法務部部長&num=100&lang=zh&ontology=True>

    ```json
    ["中華民國總統府國策顧問"],
    ["中華民國內政部部長"],
    ["中華民國法官"],
    ["中華民國檢察官"],
    ["國立臺灣大學法律學院校友"]
    ...
    etc
    ```

2. get vector：_`/kem/vector`_

  - keyword
  - example： <http://udiclab.cs.nchu.edu.tw/kem/vector?keyword=女生&lang=zh>

    ```json
    [1.3885987997055054, 0.5394280552864075, -0.2656879723072052, 0.7741730809211731, 0.591987133026123 ...]
    ```

## Experimental Feature

This feature is based on [kcem](https://github.com/UDICatNCHU/kcem)

which is a ontology with isA relation

Setting `--ontology` to True would turn all noun in the training corpus into hypernym

and concatenate this transformed corpus with original one

Finally, train word2vec with this transformed corpus.

It really enhance the original vector space.

result:

```python
>>> model.most_similar('中華民國法務部部長')
# 中華民國內政部部長 效果也不錯
[
  [
    "中華民國總統府國策顧問",
    0.7841469645500183
  ],
  [
    "中華民國內政部部長",
    0.7837527990341187
  ],
  [
    "中華民國法官",
    0.7816867828369141
  ],
  [
    "中華民國檢察官",
    0.7780462503433228
  ],
  [
    "國立臺灣大學法律學院校友",
    0.7581177949905396
  ]
]
```

origin:
```python
>>> model.most_similar('中華民國法務部部長')
[
  [
    "楊芳婉",
    0.8307946920394897
  ],
  [
    "吳朱疆",
    0.830314040184021
  ],
  [
    "郭宗德",
    0.8272522687911987
  ],
  [
    "莊懷義",
    0.8246101140975952
  ],
  [
    "蔡兆陽",
    0.821085512638092
  ]
]
```

壓縮後的model

Pearson correlation coefficient 有 0.7

```python
a = [compress.similarity('張飛', '本多忠勝'), compress.similarity('呂布', '本多忠勝'), compress.similarity('福爾摩斯改編電視劇', '狄仁傑題材電視劇'), compress.similarity('美國隊長', '蝙蝠俠'), compress.similarity('吾命騎士', '哈利波特'), compress.similarity('羅瑩雪', '金正恩')]
b = [compress.similarity('蜀漢軍事人物', '戰國武將'), compress.similarity('三國志立傳人物', '戰國武將'), compress.similarity('新福爾摩斯', '神探狄仁傑'), compress.similarity('漫威漫畫超級英雄', 'DC漫畫超級英雄'), compress.similarity('臺灣輕小說', '英國小說'), compress.similarity('中華民國法務部部長', '朝鮮勞動黨中央軍事委員會副委員長')]
from scipy.stats import pearsonr
spearmanr(a, b)
```

## Built With

python3.5

## Contributors
* __張泰瑋__ [david](https://github.com/david30907d)
* __游哲軒__ [Shane Yu](https://github.com/theshaneyu)

## License

This package use `GPL3.0` License.
