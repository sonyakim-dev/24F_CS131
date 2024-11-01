import Distribution.Simple.Setup (falseArg)
-- HASK17
longest_run :: [Bool] -> Int
-- longest_run ls = longest_run_helper ls 0 0
--   where
--     longest_run_helper [] _ m = m
--     longest_run_helper (x:xs) curr m
--       | x = longest_run_helper xs (curr + 1) (max (curr + 1) m)
--       | otherwise = longest_run_helper xs 0 (max curr m)
longest_run ls = fst (foldl (\(m, curr) x -> if x then ((max (curr+1) m), curr+1) else (m, 0)) (0, 0) ls)

data Tree = Empty | Node Integer [Tree]
  deriving Show
max_tree_value :: Tree -> Integer
max_tree_value Empty = 0
max_tree_value (Node v []) = v
-- max_tree_value (Node v (x:xs)) = max v (max (max_tree_value x) (max_tree_value (Node v xs)))
max_tree_value (Node value child) = max value (maximum (map max_tree_value child))


-- HASK18
data Event = Travel Integer | Fight Integer | Heal Integer
super_giuseppe :: [Event] -> Integer
super_giuseppe events = super_giuseppe_helper events 100 False
  where
    super_giuseppe_helper [] hp _ = hp
    super_giuseppe_helper (event:rest) hp mode
      | hp <= 0 = -1
      | otherwise =
          let (new_hp, new_mode) = handle_event event hp mode
          in super_giuseppe_helper rest new_hp new_mode
    handle_event (Travel n) hp True = (hp, True)
    handle_event (Travel n) hp False = (min 100 (hp + (n `div` 4)), False)
    handle_event (Fight n) hp True = (hp - (n `div` 2), hp - (n `div` 2) <= 40)
    handle_event (Fight n) hp False = (hp - n, hp - n <= 40)
    handle_event (Heal n) hp _ = (min 100 (hp + n), min 100 (hp + n) <= 40)


-- HASK19
sumSquares :: Integer -> Integer
sumSquares 0 = 0
-- sumSquares n = n^2 + sumSquares (n-1)
sumSquares n = sumSquares_helper n 0
  where
    sumSquares_helper 0 acc = acc
    sumSquares_helper n acc = sumSquares_helper (n-1) (acc + n^2) 


main :: IO ()
main = do
  -- print(longest_run [True, True, False, True, True, True, False])
  -- print(max_tree_value (Node 3 [(Node 2 [Node 7 []]), (Node 5 [Node 4 []])]))
  -- print(super_giuseppe [Heal 40, Fight 70, Travel 100, Fight 60, Heal 40])
  print(sumSquares 3)
