# Code for understanding behavior of LM on different data

Points to be noted: 
1. For the shorthand notation, throughout the code, we use K=-1 for the naturalistic sampling and K=0 for the selective sampling. 
2. The random seed for splitting the dataset is 40. This can be changed from the code. 
3. By default (and what is reported in the paper), we split the data into two subsets according to the count of attractors to study domain adaptation. However, the same could be done using count of intervening nouns. Therefore, to do so, just add ```--n_intervening``` at the end of the following snippet. 

## Targeted Syntactic Evaluation template Construction 
```
cd TSE/
python make_templates.py <out folder for template_dir>
python construct_tsv.py out_folder/
```
This will generate tse.tsv, containing the artifically constructed sentences, in a similar format to the training data. 

## Training the Language Model 

In the paper, we use the following architectures:
1. LSTM 
2. Ordered neurons 
3. GRU
4. Decay RNN 

However, this codebase is not just limited to the mentioned architectures, but it can also run 
1. Transformer Network (implemented in ```layers.py```)
2. [Recurrent Independent Mechanisms](https://arxiv.org/abs/1909.10893) (implemented in ```RIM.py```, taken from [here](https://github.com/dido1998/Recurrent-Independent-Mechanisms)). 

### Training... 

Make sure you have folder save_model/. To train the networks mentioned in the paper:
```
python lm.py -train expr_data/<train_file> -seed 20 -dict expr_data/vocab.pkl -word_vec_size 200 -hidden_size 650  -optim adam -layers 2 -epochs 100 -batch_size 128 -n_words -1 -save_model save_model/lstm_nat.pt -lr 0.001 --rnn_arch <RNN_ARCH> (--activation tanh)
```
1. RNN_ARCH is one from - {'LSTM', 'DRNN', 'GRU', 'ONLSTM'}
2. <train_file> defines the training setting that is to be used, is one from - {train_nat.tsv, train_sel.tsv, train_inter.tsv, train_sel2.tsv}
3. The term --activation tanh is only needed while training Decay RNN (DRNN). DRNN by default uses tanh, however relu can also be used. 

If you want to train recurrent independent mechanisms, note the following first:
1. RIM can only be trained with LSTM/GRU at the moment.
2. A RIM consists of recurrent units, sparsly communicating with each other using attention bottleneck, from which at a time only k units are active, out of total num_units. 
3. Note that, for a RIM to work the size of hidden units should be divisible by num_units. 

```
 python lm.py -train expr_data/<train_file> -seed 20 -dict expr_data/vocab.pkl -word_vec_size 200 -hidden_size 650  -optim adam -layers 2 -epochs 100 -batch_size 128 -n_words -1 -save_model save_model/lm_rim.pt -lr 0.001 --rnn_arch LSTM -arch RIM -num_units 5 -k 3
```

If want to use transformer network, use -arch fan and -num_head to specify number of attention heads. Also, occasionally if the size of hidden units is same as that of word vector size, then one can use -tied to tie the weights (often works as a regularizer).

### Testing
To test the trained model on the natural testing set:
```
python full_eval_lm.py  -checkpoint save_model/<name_of_saved_model>.pt -input expr_data/test.tsv -output o.pkl -batch_size 512 --rnn_arch LSTM --get_hidden
```
This will give the results demarcated with different number of attractors, by default. To get results demarcated with different number of attractors and intervening noun pairs, uncomment line 225. It also gives accuracy with increasing distance between the main noun and main verb (although not used in the paper). --get_hidden will save 2000 hidden units to be used for RSA. 

### Testing Synthetic sentences... 

This will generate result.tsv for each type of sentence (for example, Agreement across ORC)
```
python full_eval_lm_ood.py  -checkpoint save_models/lm_rnn.pt -input tse.tsv -output o.pkl -batch_size 512 --rnn_arch LSTM 
```

## Representation Similarity Analysis 

To Do RSA, first get the hidden units of all the models (including K=0 and K=-1, on all random seed) and collect them in a folder. for LM, use the first code and later for the BC. 

```
python RSA.py -input <folder>
python RSA_BC.py -input <folder> 
```

This will give the scaled representations of all the models, in a RSA.pkl. Rest, follow the jupyter notebook for the visualization (separate for both BC and LM). 

## Fine tuning the trained LM

In the appendix of our paper, we mention the results of fine tuning the trained LM on the artifically constructed sentences. To do so, select the templates you want to use for the construction (we did not use RCs to avoid large distribution changes). Once constructed the tse_finetune.tsv for those templates (from the method described above) use the following: 

```
python fine_tune.py  -checkpoint save_models/lm_rnn.pt  -dict expr_data/vocab.pkl -train tse_finetune.tsv -hidden_size 650 -batch_size 512 --rnn_arch DRNN --activation tanh -save_model save_model/lm_rnn_finetune.pt -epochs 1
```

This will generate the trained model as lm_rnn_finetune.pt. Now use this for desired testing! 
