

def lower_col_names(*args):
    for df in args:
        df.columns = [column.lower() for column in df.columns]


def lower_columns(df, col_names):
    for col in col_names:
        df[col] = df[col].str.lower()


def capitalize_columns_names(df, col_names):
    for col in col_names:
        df[col] = df[col].str.capitalize()
