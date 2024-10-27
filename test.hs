-- fibonacci in O(n) time
-- n: how many numbers left to compute
import Data.Char (toUpper, toLower)

fib n = _fib n 0 1
  where
    _fib 0 a _ = a
    _fib n a b = _fib (n-1) b (a+b)


addFive = (+ 5) -- same as addFive a = a + 5

f = (\g h i -> i h g) ["Carey"] [131]
-- input: function i with arguments h(["Chary"]) and g([131])
i h g = "h: " ++ show h ++ ", g: " ++ show g

swap f a b = f b a

cap_len :: [String] -> [(String, Int)]
cap_len ls = map (\(x:xs) -> (toUpper x : xs, length (x:xs))) ls

mashup s1 s2 n = take n s1 ++ reverse (take n s2)
mashup_curry = \s1 -> \s2 -> \n -> take n s1 ++ reverse (take n s2)
-- mashup_curry = (\s1 -> (\s2 -> (\n -> take n s1 ++ reverse (take n s2))))
-- in Python: mashup_curry = (lambda s1 : (lambda s2 : (lambda n : s1[:n] + s2[:n][::-1])))


data DLL =
  Nil |
  Node { prev :: DLL, value :: Int, next :: DLL}

getTailVal :: DLL -> Int
getTailVal Nil = -1
getTailVal (Node _ val Nil) = val
getTailVal (Node _ _ next) = getTailVal next

toList Nil = []
toList (Node _ val next) = val : toList next

fromList :: [Int] -> DLL
fromList [] = Nil
fromList (x:xs) = Node Nil x (fromList xs)

divis n m = [x | x <- [n..m], x `mod` 5 == 0 || x `mod` 7 == 0 || x `mod` 9 == 0]


main :: IO ()
main = do
  putStrLn (f i)
  print(cap_len ["cat", "mat", "baT_!"])
