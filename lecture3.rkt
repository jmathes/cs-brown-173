#lang plai

(define-type ExprC
  [numC (n number?)]
  [plusC (l ExprC?) (r ExprC?)]
  [multC (l ExprC?) (r ExprC?)]
  [idC (s symbol?)]
  [appC (fun symbol?) (arg ExprC?)]
  )

(define four (numC 4))
(test (numC-n four) 4)

"(interp (<substitute> a <for the arg of f> <body of the function named f>) fds)"

(define (interp arith_exp fds)
  (type-case ExprC arith_exp
    [numC (n) n]
    [plusC (l r) (+ (interp l fds) (interp r fds))]
    [multC (l r) (* (interp l fds) (interp r fds))]
    [idC (_) (error "unbound identifier")]
    [appC (f a) ( local ([define fd (get-fundef f fds)])
                   (interp (subst a (fdC-arg fd) (fdC-body fd)) fds)
                   )]
    )
  )

(define-type FunDefC
  [fdC (name symbol?) (arg symbol?) (body ExprC?)])



(define fds (list
  (fdC 'double 'x (multC (numC 2) (idC 'x)))
  (fdC 'double 'x (multC (numC 3) (idC 'x)))
  (fdC 'quadruple 'x (appC 'double (appC 'double (idC 'x))))
  (fdC 'const5 '_ (numC 5))
  ))

(define (get-fundef2 fname fds) 
  (first (filter (lambda (fd) (eq? fname (fdC-name fd))) fds))
  )

(define (get-fundef n fds)
  (cond
    [(empty? fds) (error 'get-fundef "reference to undefined function")]
    [(cons? fds) (cond
                   [(symbol=? n (fdC-name (first fds))) (first fds)]
                   [else (get-fundef n (rest fds))])]))
  

(test (fdC 'double 'x (multC (numC 2) (idC 'x))) (get-fundef 'double fds))
(test (fdC 'const5 '_ (numC 5)) (get-fundef 'const5 fds))
(test (fdC 'double 'x (multC (numC 2) (idC 'x))) (get-fundef2 'double fds))
(test (fdC 'const5 '_ (numC 5)) (get-fundef2 'const5 fds))

(define nums '(1 2 3))

(test (interp (numC 4) fds) 4)

(define five-plus-six (plusC (numC 5) (numC 6)))
(test (interp five-plus-six  fds) 11)

(test (interp (multC (numC 7) (plusC (numC 2) (numC 3))) fds) 35)

(define (subst what for in)
  (type-case ExprC in
    [numC (_) in]
    [plusC (l r) (plusC (subst what for l) (subst what for r))]
    [multC (l r) (multC (subst what for l) (subst what for r))]
    [idC (s) (cond
               [(eq? for s) what]
               [else in]
               )]
    [appC (f a) (appC f (subst what for a))]
    )
  )

(test (numC 2) (subst (numC 2) 'x (idC 'x)))
(test (multC (numC 1) (numC 1)) (subst (numC 1) 'x (multC (idC 'x) (idC 'x))))
(test 5 (interp (appC 'const5 (numC 3)) fds))
(test 8 (interp (appC 'quadruple (numC 2)) fds))

(define-type ExprS
  [numS (n number?)]
  [plusS (l ExprS?) (r ExprS?)]
  [multS (l ExprS?) (r ExprS?)]
  [idS (i symbol?)]
    
  [uminusS (n ExprS?)]
  [bminusS (l ExprS?) (r ExprS?)]
  )

(define (desugar arith_sugar)
  (type-case ExprS arith_sugar
    [numS (n) (numC n)]
    [plusS (l r) (plusC (desugar l) (desugar r))]
    [multS (l r) (multC (desugar l) (desugar r))]
    [idS (s) (error "unbound identifier")]
    
    [uminusS (n) (desugar (multS (numS -1) n))]
    [bminusS (l r) (plusC (desugar l) (multC (numC -1) (desugar r)))]
    )
  )

(test (desugar (numS 3)) (numC 3))
(test (desugar (bminusS (numS 3) (numS 2))) (plusC (numC 3) (multC (numC -1) (numC 2))))
(test (interp (desugar (uminusS (numS 8))) '()) -8)

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