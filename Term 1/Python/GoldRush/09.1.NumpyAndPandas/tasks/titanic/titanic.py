import typing as tp

import pandas as pd


def male_age(df: pd.DataFrame) -> float:
    """
    Return mean age of survived men, embarked in Southampton with fare > 30
    :param df: dataframe
    :return: mean age
    """
    subset = df[
        (df['Survived'] == 1) &
        (df['Sex'] == 'male') &
        (df['Embarked'] == 'S') &
        (df['Fare'] > 30)
    ]
    return float(subset['Age'].mean())


def nan_columns(df: pd.DataFrame) -> tp.Iterable[str]:
    """
    Return list of columns containing nans
    :param df: dataframe
    :return: series of columns
    """
    return [str(col) for col in df.columns[df.isna().any()]]


def class_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Return Pclass distrubution
    :param df: dataframe
    :return: series with ratios
    """
    return df['Pclass'].value_counts(normalize=True).sort_index()


def families_count(df: pd.DataFrame, k: int) -> int:
    """
    Compute number of families with more than k members
    :param df: dataframe,
    :param k: number of members,
    :return: number of families
    """
    family_counts = df['Name'].str.split(',').str[0].value_counts()
    return int(len(family_counts[family_counts > k]))

def mean_price(df: pd.DataFrame, tickets: tp.Iterable[str]) -> float:
    """
    Return mean price for specific tickets list
    :param df: dataframe,
    :param tickets: list of tickets,
    :return: mean fare for this tickets
    """
    subset = df[df['Ticket'].isin(list(tickets))]
    return float(subset['Fare'].mean())


def max_size_group(df: pd.DataFrame, columns: list[str]) -> tp.Iterable[tp.Any]:
    """
    For given set of columns compute most common combination of values of these columns
    :param df: dataframe,
    :param columns: columns for grouping,
    :return: list of most common combination
    """
    res = df.groupby(columns).size().idxmax()
    if isinstance(res, tuple):
        return res
    return (res,)


def dead_lucky(df: pd.DataFrame) -> float:
    """
    Compute dead ratio of passengers with lucky tickets.
    A ticket is considered lucky when it contains an even number of digits in it
    and the sum of the first half of digits equals the sum of the second part of digits
    ex:
    lucky: 123222, 2671, 935755
    not lucky: 123456, 62869, 568290
    :param df: dataframe,
    :return: ratio of dead lucky passengers
    """

    def is_lucky(ticket: tp.Any) -> bool:
        s = str(ticket)
        if not s.isdigit() or len(s) % 2 != 0:
            return False
        half = len(s) // 2
        try:
            first_half = sum(int(digit) for digit in s[:half])
            second_half = sum(int(digit) for digit in s[half:])
            return first_half == second_half
        except ValueError:
            return False
    lucky_passengers = df[df['Ticket'].apply(is_lucky)]

    if len(lucky_passengers) == 0:
        return 0.0

    dead_lucky_count = len(lucky_passengers[lucky_passengers['Survived'] == 0])
    return float(dead_lucky_count / len(lucky_passengers))
