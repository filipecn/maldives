#!/usr/bin/python

import numpy as np
import pandas as pd
import okane.io as io
import re
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
from sklearn.model_selection import train_test_split

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


def cleanup_data(data):
    descriptor = Descriptor()
    descriptor.add_rule(Rule(r"[^\w\s]", r" "))
    descriptor.add_rule(Rule(r"\d+", r" "))
    descriptor.add_rule(Rule(r"IRVINE", r" "))
    descriptor.add_rule(Rule(r" \w{2}($| )", r" "))
    descriptor.add_rule(Rule(r" \w{1}($| )", r" "))

    data["desc"] = [descriptor.compute(x) for x in data[io.IOColumns.DESCRIPTION]]

    return data


def compute_one_hot_matrix(corpus):
    # Create a set of unique words in the corpus
    unique_words = set()
    for sentence in corpus:
        for word in sentence.split():
            unique_words.add(word.lower())

    # unique word to an index
    word_to_index = {}
    for i, word in enumerate(unique_words):
        word_to_index[word] = i

    # Create one-hot encoded vectors for
    # each word in the corpus
    one_hot_vectors = []
    for sentence in corpus:
        vector = np.zeros(len(unique_words))
        for word in sentence.split():
            vector[word_to_index[word.lower()]] = 1
        one_hot_vectors.append(vector)

    one_hot_matrix = pd.DataFrame(one_hot_vectors, columns=list(unique_words))
    one_hot_matrix["count"] = one_hot_matrix.sum(axis=1, numeric_only=True)
    one_hot_matrix["desc"] = corpus

    return one_hot_matrix


class OneHotMatrix:
    def __init__(self, path):
        df = pd.read_csv(path)
        df = cleanup_data(self.df)

        # self.one_hot_matrix = compute_one_hot_matrix(self.df["desc"])
        # self.x = self.one_hot_matrix.drop(columns=["count", "desc"])
        # self.y = self.df[io.IOColumns.CATEGORY]

        label_map = {
            cat: index for index, cat in enumerate(np.unique(df[io.IOColumns.CATEGORY]))
        }

        num_classes = len(label_map)

        def one_hot_label(label):
            label = tf.one_hot(label, num_classes)
            return label

        df["one_hot_label"] = [
            one_hot_label(label_map[x]) for x in df[io.IOColumns.CATEGORY]
        ]

        df_train, df_test = train_test_split(df, test_size=0.2, random_state=1)

        y_train = np.asarray(df_train["one_hot_label"])
        y_test = np.asarray(df_test["one_hot_label"])

        max_words = 300

        tokenizer = Tokenizer(num_words=max_words)
        tokenizer.fit_on_texts(df_train["desc"].values)

        sequences_train = tokenizer.texts_to_sequences(df_train["desc"].values)
        sequences_test = tokenizer.texts_to_sequences(df_test["desc"].values)

        X_train = pad_sequences(sequences_train, maxlen=max_words_by_sentence)
        X_test = pad_sequences(sequences_test, maxlen=max_words_by_sentence)

        print(X_train.shape)
        print(X_test.shape)
        print(label_map)
