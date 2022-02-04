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
    """iterates over excel colnames lowercase"""
    import string
    from itertools import product
    ua = string.ascii_lowercase
    yield from ua
    for i in count(2):
        yield from product(ua, repeat=i)

from sklearn.tree import _tree
def tree2vis(tree, feature_names, target_name='Fraud'):
    """Converts scikit learn decision tree to both mermaid & cytoscape formats for visualization"""
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
    cyto_nodes = []
    cyto_edges = []
    count_iter = count(0)
    node2varname = {}
    def walk(node):
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            treshold = tree_.threshold[node]
            X = "".join(next(e_iter))
            feature2letter[name]=X
            node2varname[X] = name
            if abs(treshold - 0.5) < 0.01:
                cyto_nodes.append({"data": {"id": X, "label": name}})
            else:
                cyto_nodes.append({"data": {"id": X, "label": "%.1f" %treshold}}) # "%s @ %.1f" %(name, treshold)}})
            seen_features.add(name)
            f1 = "{X}[{name}]".format(X=X, name=name)
            write(f1)
            write(";\n")
            try:
                cyto_edges[-1]['data']['target']=X
                cyto_edges[-1]['data']['id'] += ("%s_%d" % (X, next(count_iter)))
            except:
                pass
            write("{f1}-->|{thresh}| ".format(f1=f1, thresh="<=%.1f" % treshold))
            cyto_edges.append({"data": {"id":"%s1"% X,"source": X, "label":"%s <= %.1f" % (name, treshold)}})
            walk(tree_.children_left[node])
            write(";\n")
            write("{f1}-->|{thresh}| ".format(f1="{X}[{name}]".format(X=X, name=name), thresh=">%.1f" % treshold))
            cyto_edges.append({"data": {"id":"%s9"% X,"source": X, "label":"> %.1f" % treshold}})
            walk(tree_.children_right[node])
        else:
            results = tree_.value[node][0]
            name = target_name+": "+str(results[0] > results[1])
            if name in seen_features:
                X = feature2letter[name]
                cyto_edges[-1]['data']['target']=X
                f1 = "{X}[{name}]".format(X=X, name=name)
                write(f1)
            else:
                X = "".join(next(e_iter))
                feature2letter[name]=X
                cyto_nodes.append({"data": {"id": X, "label": name}})
                cyto_edges[-1]['data']['target']=X
                seen_features.add(name)
                f1 = "{X}[{name}]".format(X=X, name=name)
                write(f1)
    walk(0)
    contents = output.getvalue()
    output.close()
    st = contents.index("\n")
    return {"mermaid":"graph TD;\n" +contents[st+1:], 
             "cyto":cyto_nodes+cyto_edges,
             "node2varname":node2varname}

def determine_next(df1, node_id):
    branches = [r for r in vis_data['cyto'] if ('source' in r['data']) and  (r['data']['source']==node_id)]
    if any(df1.eval(branches[0]['data']['label'])):
        return branches[0]['data']['target']
    else:
        return branches[1]['data']['target']

def get_tree_path(df1):
    path = ['a']
    try:
        while True:
            path.append(determine_next(df1, path[-1]))
    except:
        pass
    return path
    
def find_edge(cyto, source, target):
    for row in cyto:
        if 'source' in row['data']:
            if row['data']['source'] == source:
                if row['data']['target'] == target:
                    return row

def color_decision_path(df1):
    path = get_tree_path(df1)
    cyto = tree2vis(clf, dependent_vars)['cyto'].copy()
    for source,target in zip(path, path[1:]):
        find_edge(cyto, source, target)["classes"]='green'
    return cyto

from dash import Dash,html
from dash_extensions import Mermaid
import dash_cytoscape as cyto

cyto.load_extra_layouts()
app = Dash()

vis_data = tree2vis(clf, dependent_variables)
app.layout = html.Div([
Mermaid(chart=vis_data['mermaid']),
cyto.Cytoscape(
                id="decision-tree",
                layout={"name": "dagre"},
                style={"width": "100%", "height": "400px"},
                elements=vis_data['cyto'],
            )
])
            

if __name__ == "__main__":
    app.run_server()
