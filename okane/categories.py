#!/usr/bin/python

import numpy as np
import pandas as pd
import okane.io as io
import re
from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import tensorflow as tf

from okane.io import IOColumns

g_category_names = [
    "Rent",
    "Home Improvement",
    "Home Maintenance",
    "Mortgages",
    "Furnitures",
    "Utilities",
    "Internet",
    "Gas",
    "Water",
    "Electricity",
    "Telephone",
    "Gasoline/Fuel",
    "Automotive Expenses",
    "Car Payments",
    "Public Transportation",
    "Bike",
    "Private Transportation",
    "Market",
    "Child/Dependent Expenses",
    "Personal Care",
    "Pets/Pet Care",
    "Pharmacy",
    "Healthcare/Medical",
    "Fitness or Health club membership",
    "Insurance",
    "Home Insurance",
    "Life Insurance",
    "Auto Insurance",
    "Restaurants",
    "Cofee Shops",
    "Fast Food",
    "Hobbies",
    "Clothing/Shoes",
    "Electronics",
    "Entertainment",
    "General Merchandise",
    "Gifts",
    "Online Services",
    "Flights",
    "Hotels",
    "Car Rentals",
    "ATM/Cash Withdrawals",
    "Checks",
    "Other Bills",
    "Other Expenses",
    "Charity",
    "Business Miscellaneous",
    "Dues & Subscriptions",
    "Office Maintenance",
    "Office Supplies",
    "Postage & Shipping",
    "Printing",
    "Tuition",
    "Online Courses",
    "Savings",
    "Credit Card Payments",
    "Investment Account Fees/Charges",
    "Loans",
    "Service Charges/Fees",
    "Taxes",
    "Paycheck",
    "Bonus",
    "Interest",
    "Allowances",
    "Reimbursements",
    "Uncategorized",
]

g_category_groups = [
    "Home & Utilities",
    "Home & Utilities",
    "Home & Utilities",
    "Home & Utilities",
    "Home & Utilities",
    "Home & Utilities",
    "Home & Utilities",
    "Home & Utilities",
    "Home & Utilities",
    "Home & Utilities",
    "Home & Utilities",
    "Transportation",
    "Transportation",
    "Transportation",
    "Transportation",
    "Transportation",
    "Transportation",
    "Groceries",
    "Personal & Family Care",
    "Personal & Family Care",
    "Personal & Family Care",
    "Health",
    "Health",
    "Health",
    "Health",
    "Insurance",
    "Insurance",
    "Insurance",
    "Restaurants & Dining",
    "Restaurants & Dining",
    "Restaurants & Dining",
    "Shopping & Entertainment",
    "Shopping & Entertainment",
    "Shopping & Entertainment",
    "Shopping & Entertainment",
    "Shopping & Entertainment",
    "Shopping & Entertainment",
    "Shopping & Entertainment",
    "Travel",
    "Travel",
    "Travel",
    "Cash, Checks & Misc",
    "Cash, Checks & Misc",
    "Cash, Checks & Misc",
    "Cash, Checks & Misc",
    "Giving",
    "Business Expenses",
    "Business Expenses",
    "Business Expenses",
    "Business Expenses",
    "Business Expenses",
    "Business Expenses",
    "Education",
    "Education",
    "Finance",
    "Finance",
    "Finance",
    "Finance",
    "Finance",
    "Finance",
    "Income",
    "Income",
    "Income",
    "Income",
    "Income",
    "Uncategorized",
]

g_group_names = [
    "Category",
    "Home & Utilities",
    "Transportation",
    "Groceries",
    "Personal & Family Care",
    "Health",
    "Insurance",
    "Restaurants & Dining",
    "Shopping & Entertainment",
    "Travel",
    "Cash, Checks & Misc",
    "Giving",
    "Business Expenses",
    "Education",
    "Finance",
    "Income",
]

g_group_descriptions = [
    "Includes rent, mortgage, utilities, phone, cable, maintenance, and home improvement.",
    "Includes car payments, gas, public transportation, and other auto expenses.",
    "Includes food. It does not include restaurants or coffee shops.",
    "Includes personal care, pet care, and child care.",
    "Includes insurance, doctor visits, medical expenses and fitness or health club dues.",
    "Includes home, auto, renters, personal property and life insurance payments.",
    "Includes restaurants, coffee shops, and fast food.",
    "Includes clothing, shoes, electronics, entertainment, gifts, hobbies, and other shopping.",
    "Includes flights, hotels, and car rentals.",
    "Includes ATM withdrawals, checks and other expenses.",
    "Includes charitable giving.",
    "Includes office maintenance, supplies, postage, printing, dues, and other business expenses.",
    "Includes tuition, online courses, campus bookstores, and student loans.",
    "Includes service charges and fees, taxes, loan payments, credit card payments, and may include investment account fees and charges if applicable.",
    "Includes paychecks, bonus, reibursements",
]


class Rule:
    def __init__(self, pattern: list, repl: str):
        self.pattern = pattern
        self.repl = repl

    def apply(self, s: str):
        replacing = True
        ans = s
        while replacing:
            replacing = False
            new_ans = re.sub(self.pattern, self.repl, ans)
            if new_ans != ans:
                replacing = True
            ans = new_ans
        return ans


class Descriptor:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def compute(self, text: str):
        ans = text.upper()
        for rule in self.rules:
            ans = rule.apply(ans)
        return ans


def process_descriptions(data) -> pd.DataFrame:
    """
    Cleanup transaction text by running a set of Descriptor rules.

    :param DataFrame data: Transaction history with the description column.
    :return: copy of data with an extra column "desc" containing the generated
             description.
    """
    descriptor = Descriptor()
    descriptor.add_rule(Rule(r"[^\w\s]", r" "))
    descriptor.add_rule(Rule(r"\d+", r" "))
    descriptor.add_rule(Rule(r"IRVINE", r" "))
    descriptor.add_rule(Rule(r" \w{2}($| )", r" "))
    descriptor.add_rule(Rule(r" \w{1}($| )", r" "))

    data["desc"] = [descriptor.compute(x) for x in data[io.IOColumns.DESCRIPTION]]

    return data


def create_rnn_model(input_size, output_size):
    ## Define the embedding dimension
    EMBEDDING_DIM = 128

    rnn = keras.Sequential()

    print(input_size, output_size)
    rnn.add(keras.layers.Input(shape=(input_size,)))
    rnn.add(keras.layers.BatchNormalization())
    rnn.add(keras.layers.Dense(20, activation="relu", name="dense_layer_1"))
    rnn.add(keras.layers.Dense(10, activation="relu", name="dense_layer_2"))
    rnn.add(keras.layers.Dense(output_size, activation="softmax", name="output"))

    return rnn


def train_model(x, y, label_count):

    BATCH_SIZE = 128
    EPOCHS = 20
    VALIDATION_SPLIT = 0.2

    y_one_hot = tf.one_hot(y, label_count)

    model = create_rnn_model(x.shape[1], label_count)
    print(model.summary())
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
    model_fit = model.fit(
        x,
        y_one_hot,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        verbose=2,
        validation_split=VALIDATION_SPLIT,
    )

    return model


def test_model(model, x_test, y_test, label_count):
    results = model.evaluate(x_test, tf.one_hot(y_test, label_count), batch_size=128)
    print("test loss, test acc:", results)
    prediction = model.predict(x_test[:1])
    print("prediction shape:", prediction.shape)
    print(prediction)


class Classifier:
    def __init__(self, path):

        # read labeled data
        df = pd.read_csv(path)

        # generate clean descriptions
        df = process_descriptions(df)

        # retrieve list of labels from Category data
        label_map = {
            cat: index for index, cat in enumerate(np.unique(df[io.IOColumns.CATEGORY]))
        }
        df["y"] = [label_map[x] for x in df[io.IOColumns.CATEGORY]]

        # prepare learn data
        df_train, df_test = train_test_split(df, test_size=0.2, random_state=1)

        # X

        # setup parameters
        max_words = 300
        max_words_by_sentence = 10
        # retrieve vocab from "desc" data
        tokenizer = Tokenizer(num_words=max_words)
        tokenizer.fit_on_texts(df_train["desc"].values)
        # generate word id sequences for train and test sets
        sequences_train = tokenizer.texts_to_sequences(df_train["desc"].values)
        sequences_test = tokenizer.texts_to_sequences(df_test["desc"].values)
        # normalize sequence sizes
        x_train = pad_sequences(sequences_train, maxlen=max_words_by_sentence).astype(
            "int32"
        )
        x_test = pad_sequences(sequences_test, maxlen=max_words_by_sentence).astype(
            "int32"
        )

        # y

        y_train = np.asarray(df_train["y"])
        y_test = np.asarray(df_test["y"])

        model = train_model(x_train, y_train, len(label_map))
        test_model(model, x_test, y_test, len(label_map))
