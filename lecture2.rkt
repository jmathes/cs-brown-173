#lang plai

(define-type ArithC
  [numC (n number?)]
  [plusC (l ArithC?) (r ArithC?)]
  [multC (l ArithC?) (r ArithC?)])

(define four (numC 4))
(test (numC-n four) 4)


(define (interp arith_exp)
  (type-case ArithC arith_exp
    [numC (n) n]
    [plusC (l r) (+ (interp l) (interp r))]
    [multC (l r) (* (interp l) (interp r))]
    )
  )

(test (interp four) 4)

(define five-plus-six (plusC (numC 5) (numC 6)))
(test (interp five-plus-six) 11)

(test (interp (multC (numC 7) (plusC (numC 2) (numC 3)))) 35)


(define-type ArithS
  [numS (n number?)]
  [plusS (l ArithS?) (r ArithS?)]
  [multS (l ArithS?) (r ArithS?)]
  [bminusS (l ArithS?) (r ArithS?)]
  )

(define (desugar arith_sugar)
  (type-case ArithS arith_sugar
    [numS (n) (numC n)]
    [plusS (l r) (plusC (desugar l) (desugar r))]
    [multS (l r) (multC (desugar l) (desugar r))]
    [bminusS (l r) (plusC (desugar l) (multC (numC -1) (desugar r)))]
    )
  )

(test (desugar (numS 3)) (numC 3))
(test (desugar (bminusS (numS 3) (numS 2))) (plusC (numC 3) (multC (numC -1) (numC 2))))

(define (parse e)
  (cond
    [(number? e) (numC e)]
    [(list? e)
     (case (first e)
       [(+) (plusC (parse (second e)) (parse (third e)))]
       [(*) (multC (parse (second e)) (parse (third e)))]
       )
     ]
    )
  )

(test 3 (parse 3))(test (desugar (numS 3)) (numC 3))
(test 5 (interp (parse '(+ 3 2))))