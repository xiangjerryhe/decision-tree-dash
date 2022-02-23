__author__ = "Jerry He"
def excel_colname_iter():
    """iterates over excel colnames lowercase"""
    import string
    from itertools import product
    ua = string.ascii_lowercase
    yield from ua
    for i in count(2):
        yield from product(ua, repeat=i)
 
_pat = re.compile(r'(?<!^)(?=[A-Z])')
def camelCase2_(name):
    return _pat.sub('_', name).lower()

from sklearn.tree import _tree
from collections import defaultdict
import sys  
def rf2vis(rf_model, feature_names, target_name='Survived'):
    """Converts scikit-learn Random Forest model to cytoscape formats for visualization"""
    from sklearn.tree import _tree
    feature2letter = {}
    seen_features = set()
    e_iter = excel_colname_iter()
    def walk(node, tree_idx=0):
        tree_ = rf_model.estimators_[tree_idx].tree_    
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            print(name)
            treshold = tree_.threshold[node]
            X = "".join(next(e_iter))
            feature2letter[name]=X
            node2varname[X] = name
            cyto_nodes.append({"data": {"id": X, "label": camelCase2_(name_).replace("_"," ")}, "classes":"multiline-auto"})
            seen_features.add(name)
            f1 = "{X}[{name}]".format(X=X, name=name)
            write(f1)
            write(";\n")
            try:
                cyto_edges[-1]['data']['target']=X
                cyto_edges[-1]['data']['id'] += ("%s_%d" % (X, next(count_iter)))
            except:
                pass
            print(treshold)
            write("{f1}-->|{thresh}| ".format(f1=f1, thresh="<=%.1f" % treshold))
            print(X)
            cyto_edges.append({"data": {"id":"%s1"% X,"source": X, "label":"<=%.1f" % treshold},
                                "classes":"purple"})
            walk(tree_.children_left[node], tree_idx)
            write(";\n")
            write("{f1}-->|{thresh}| ".format(f1="{X}[{name}]".format(X=X, name=name), thresh=">%.1f" % treshold))
            cyto_edges.append({"data": {"id":"%s9"% X,"source": X, "label":"> %.1f" % treshold},
                                "classes":"purple"})
            walk(tree_.children_right[node], tree_idx)
        else:
            results = tree_.value[node][0]
            name = target_name+": "+str(results[0] < results[1])
            is_fraud = results[0] < results[1]
            if name in seen_features:
                X = feature2letter[name]
                cyto_edges[-1]['data']['target']=X
                f1 = "{X}[{name}]".format(X=X, name=name)
                write(f1)
            else:
                X = "".join(next(e_iter))
                feature2letter[name]=X
                node2varname[X] = name
                if is_fraud:
                    cyto_nodes.append({"data": {"id": X, "label": name}, "classes":"red"})
                else:
                    cyto_nodes.append({"data": {"id": X, "label": name}, "classes":"green"})
                cyto_edges[-1]['data']['target']=X
                cyto_edges[-1]['classes']= 'purple'
                seen_features.add(name)
                f1 = "{X}[{name}]".format(X=X, name=name)
                write(f1)
