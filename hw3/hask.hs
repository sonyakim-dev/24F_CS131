import Distribution.Compat.Lens (use, _1)
-- -- HASK10
scale_nums :: [Integer] -> Integer -> [Integer]
scale_nums ls factor = map (* factor) ls

only_odds :: [[Integer]] -> [[Integer]]
only_odds ls = filter (\l -> all (\x -> x`mod` 2 /= 0) l) ls
-- only_odds ls = filter (\l -> all (odd) l) ls

largest :: String -> String -> String
largest first second = if length first >= length second then first else second
largest_in_list :: [String] -> String
largest_in_list ls = foldl largest "" ls


-- -- HASK11
count_if :: (a -> Bool) -> [a] -> Int
count_if _ [] = 0
count_if f (x:xs) = (if f x then 1 else 0) + count_if f xs

count_if_with_filter :: (a -> Bool) -> [a] -> Int
count_if_with_filter f ls = length (filter f ls)

count_if_with_fold :: (a -> Bool) -> [a] -> Int
count_if_with_fold f ls = foldl (\acc -> (\x -> if f x then acc + 1 else acc)) 0 ls


-- -- HASK12
f a b =
  let c = \a -> a -- (1)
      d = \c -> b -- (2)
  in \e f -> c d e --(3)


-- -- HASK14
foo :: Integer -> Integer -> Integer -> (Integer -> a) -> [a]
-- foo x y z t = map t [x,x+z..y]
foo = \x -> \y -> \z -> \t -> map t [x,x+z..y]

bar :: (Integer -> a) -> [a]
bar = foo 1 2 3


-- -- HASK15
data InstagramUser = Influencer [String] [InstagramUser] | Normie

-- lit_collab :: InstagramUser -> InstagramUser -> Bool
-- lit_collab Influencer Influencer = True
-- lit_collab _ _ = False

-- is_sponser :: InstagramUser -> String -> Bool
-- is_sponser Normie _ = False
-- is_sponser (Influencer sponsers) sponsor = elem sponser sponsers

count_influencers :: InstagramUser -> Int
count_influencers Normie = 0
count_influencers (Influencer _ followers) = length [f | f@(Influencer _ _) <- followers]


-- -- HASK16
data LinkedList = EmptyList | ListNode Integer LinkedList
  deriving Show

ll_contains :: LinkedList -> Integer -> Bool
ll_contains EmptyList _ = False
ll_contains (ListNode val next) target = val == target || ll_contains next target

ll_insert :: LinkedList -> Integer -> Integer -> LinkedList
ll_insert ll index val = insert_helper ll index val 0
  where
    insert_helper EmptyList index val _ = ListNode val EmptyList
    insert_helper ll@(ListNode v n) index val curr
      | index <= curr = ListNode val ll
      | otherwise = ListNode v (insert_helper n index val (curr + 1))


main :: IO ()
main = do
  print(ll_insert (ListNode 3 (ListNode 6 EmptyList)) 3 4)
