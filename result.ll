@x = common global i32 0, align 4

define i32 @main() {
    store i32 10, i32* @x, align 4
    %1 = load i32, i32* @x, align 4
    %2 = shl i32 %1, 3
    store i32 %2, i32* @x, align 4
    %3 = load i32, i32* @x, align 4
    %4 = ashr i32 %3, 2
    store i32 %4, i32* @x, align 4
    %5 = load i32, i32* @x, align 4
    %6 = shl i32 %5, 5
    store i32 %6, i32* @x, align 4
    ret i32 0
}

