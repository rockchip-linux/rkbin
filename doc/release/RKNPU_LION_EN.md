# RKNPU_LION Release Note

## rknpu_lion_bl32_v2.03.bin

| Date       | File                      | Build commit | Severity  |
| ---------- | :------------------------ | ------------ | --------- |
| 2024-10-31 | rknpu_lion_bl32_v2.03.bin | 9f2aca7d1    | important |

### New

1. Add support for soft ta encryption key.
2. RPMB support read data to multiple times.
3. Optimization parameter check to enhance security.
4. Support printing TEE memory usage information.
5. Hardware crypto supports addresses exceeding 4G.
6. Support printing FWVER information.

------

## rknpu_lion_bl32_v2.02.bin

| Date       | File                      | Build commit | Severity  |
| ---------- | :------------------------ | ------------ | --------- |
| 2023-08-28 | rknpu_lion_bl32_v2.02.bin | b5340fd65    | important |

### New

1. Support pstore for optee log.
2. Enable dynamic SHM.
3. Support check ta encryption key is written.

------

## rknpu_lion_bl32_v2.01.bin

| Date       | File                      | Build commit | Severity  |
| ---------- | :------------------------ | ------------ | --------- |
| 2022-09-16 | rknpu_lion_bl32_v2.01.bin | d84087907    | important |

### Fixed

| Index | Severity  | Update                                                       | Issue description                                            | Issue source |
| ----- | --------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------ |
| 1     | important | Solve the problem that OPTEE is stuck during startup when printing is closed | User use /rkbin/tools/ddrbin_tool to close printing ,  then rk_atags will notify OPTEE to disable printing, When OPTEE starts, it will be stuck and unable to enter U-Boot | -            |

------
