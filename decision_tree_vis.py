__author__ = "Jerry He"
import pandas as pd
dat = pd.read_csv("titanic.csv")


dat['Age'] = dat['Age'].astype(float) 
dat['Fare'] = dat['Fare'].astype(float) 

cat_vars = ['Pclass', 'Embarked', 'Sex']

dat['title'] = dat['Name'].apply(lambda name: name.split(",")[1].strip().split(" ")[0])


low_count_titles = dat['title'].value_counts()[dat['title'].value_counts() < 40].index.tolist()



dat.loc[dat['title'].isin(low_count_titles), 'title'] ="other"

# Fill Age NA according to title

age_iterp = dat.groupby('title').agg({'Age':'mean'})['Age']


for (title, pred_age) in zip(age_iterp.index.tolist(), age_iterp):
    print(title, pred_age)
    dat.loc[(dat.title==title) * dat.Age.isna(), "Age"] = pred_age


# Onehot encoding
newdat = pd.get_dummies(dat, columns=cat_vars+['title'])


derived = [c for c in newdat.columns.tolist() if '_' in c]


newdat[derived].sum()



columns2drop = ['Pclass_2', 'Embarked_Q', 'Sex_female', 'Sex_female', 'title_other']



newdat.drop(columns=columns2drop, inplace=True)


dependent_variables = ['Age','Fare', 'Pclass_1',
 'Pclass_3',
 'Embarked_C',
 'Embarked_S',
 'Sex_male',
 'title_Master.',
 'title_Miss.',
 'title_Mr.',
 'title_Mrs.']


from sklearn import tree
clf = tree.DecisionTreeClassifier(max_depth=4)
clf.fit(newdat[dependent_variables], newdat['Survived'])



def excel_colname_iter():
    import string
    from itertools import product
    ua = string.ascii_uppercase
    yield from ua
    for i in count(2):
        yield from product(ua, repeat=i)

def tree_to_mermaid(tree, feature_names, target_name='Survived'):
    from sklearn.tree import _tree
    import sys
    tree_ = tree.tree_
    feature2letter = {}
    seen_features = set()
    e_iter = excel_colname_iter()
    from io import StringIO
    output = StringIO()
    write = output.write
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    def walk(node):
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            treshold = tree_.threshold[node]
            X = next(e_iter)
            feature2letter[name]=X
            seen_features.add(name)
            f1 = "{X}[{name}]".format(X=X, name=name)
            write(f1)
            write(";\n")
            write("{f1}-->|{thresh}| ".format(f1=f1, thresh="<=%.1f" % treshold))
            walk(tree_.children_left[node])
            write(";\n")
            write("{f1}-->|{thresh}| ".format(f1="{X}[{name}]".format(X=X, name=name), thresh=">%.1f" % treshold))
            walk(tree_.children_right[node])
        else:
            name = target_name+": "+str((tree_.value[node][0]>0.001)[0])
            if name in seen_features:
                X = feature2letter[name]
                f1 = "{X}[{name}]".format(X=X, name=name)
                write(f1)
            else:
                X = next(e_iter)
                feature2letter[name]=X
                seen_features.add(name)
                f1 = "{X}[{name}]".format(X=X, name=name)
                write(f1)
    walk(0)
    contents = output.getvalue()
    output.close()
    st = contents.index("\n")
    return "graph TD;\n" +contents[st+1:]

from dash import Dash
from dash_extensions import Mermaid

app = Dash()
app.layout = Mermaid(chart=tree_to_mermaid(clf, dependent_variables))

if __name__ == "__main__":
    app.run_server()


