# PX30 Release Note

## px30_bl32_v2.14.bin

| Date       | File                | Build commit | Severity  |
| ---------- | :------------------ | ------------ | --------- |
| 2022-09-16 | px30_bl32_v2.14.bin | d84087907    | important |

### Fixed

| Index | Severity  | Update                                                       | Issue description                                            | Issue source |
| ----- | --------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------ |
| 1     | important | Solve the problem that OPTEE is stuck during startup when printing is closed | User use /rkbin/tools/ddrbin_tool to close printing ,  then rk_atags will notify OPTEE to disable printing, When OPTEE starts, it will be stuck and unable to enter U-Boot | -            |

------

