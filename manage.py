#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from paraphraserApp import myclass
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm_notebook as tqdm
import joblib
import torch
import tensorflow as tf
from transformers import T5Tokenizer, AutoTokenizer,MT5Tokenizer
from transformers import MT5ForConditionalGeneration, AdamW

import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint

from transformers import AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer

# pl.seed_everything(42)
tf.random.set_seed(42)
import warnings
warnings.filterwarnings("ignore")




# DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu') 
INPUT_MAX_LEN = 256 # Input length
OUT_MAX_LEN = 128 # Output Length
TRAIN_BATCH_SIZE = 16 # Training Batch Size
VALID_BATCH_SIZE = 8 # Validation Batch Size
EPOCHS = 5 # Number of Iteration
learning_rate=1e-4
weight_decay=0.1
adam_epsilon=1e-8
gradient_accumulation_steps=16
fp_16=False


MODEL_NAME = "google/mt5-base"
tokenizer_name_or_path="google/mt5-base"
tokenizer = MT5Tokenizer.from_pretrained(MODEL_NAME, model_max_length= INPUT_MAX_LEN)


class MT5Model(pl.LightningModule):
    
    def __init__(self):
        super().__init__()
        self.model = MT5ForConditionalGeneration.from_pretrained(MODEL_NAME, return_dict=True)

    def forward(self, input_ids, attention_mask, labels=None):

        output = self.model(
            input_ids=input_ids, 
            attention_mask=attention_mask, 
            labels=labels
        )

        return output.loss, output.logits


    def training_step(self, batch, batch_idx):

        input_ids = batch["inputs_ids"]
        attention_mask = batch["attention_mask"]
        labels= batch["targets"]
        loss, outputs = self(input_ids, attention_mask, labels)

        
        self.log("train_loss", loss,on_step=True,on_epoch=True,prog_bar=True, logger=True)
        
        
        return loss


    def validation_step(self, batch, batch_idx):
        input_ids = batch["inputs_ids"]
        attention_mask = batch["attention_mask"]
        labels= batch["targets"]
        loss, outputs = self(input_ids, attention_mask, labels)

        self.log("val_loss", loss,on_epoch=True, prog_bar=True, logger=True)
        
        return loss


    def configure_optimizers(self):
        "Prepare optimizer and schedule (linear warmup and decay)"

        model = self.model
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": weight_decay,
            },
            {
                "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.1,
            },
        ]
        optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate, eps=adam_epsilon)
        self.opt = optimizer
        return [optimizer]
        # return AdamW(self.parameters(), lr=0.0001)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paraphraserDeploy.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    
    main()
