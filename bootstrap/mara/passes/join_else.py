'''
AST Rewrite Pass to join Else nodes
'''

from ..util.dispatch import method_store, multimethod
from .. import node


class JoinElse(object):
    _store = method_store()

    @multimethod(_store)
    def visit(self, n):
        pass

    @visit.d(node.Block)
    def _(self, n):
        self.scan(n.exprs)

    @visit.d(node.Module)
    def _(self, n):
        self.scan(n.exprs)

    def scan(self, exprs):
        '''
        Scan a list of exprs, joining neighboring If and Else nodes into a single IfElse node.
        The 'hole' left by the Else is replaced with a NoOp.
        To simplify generation, If nodes are transformed into IfElse nodes with a NoOp else_body.
        '''

        prev = None
        for j in range(1, len(exprs)):
            i = j - 1

            prev = exprs[i]
            curr = exprs[j]

            if isinstance(prev, node.If):

                if isinstance(curr, node.Else):
                    exprs[i] = node.IfElse(
                        pred=prev.pred,
                        if_body=prev.body,
                        else_body=curr.body,
                    )

                    exprs[j] = node.NoOp()

                else:
                    exprs[i] = node.IfElse(
                        pred=prev.pred,
                        if_body=prev.body,
                        else_body=node.NoOp(),
                    )
