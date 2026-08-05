"""In-process tests for the pure validation helpers in quake_loyola.cli
(_parse_bool, _validate_one), plus a handful of typer.testing.CliRunner
invocations for the config_show/get/set/reset/path commands and the `gen`
command's success path. These run in this process (unlike
tests/test_cli.py's subprocess-based end-to-end tests), so both correctness
and coverage instrumentation see them.

config.CONFIG_PATH is a single path fixed for the whole test session by
tests/conftest.py (an isolated, empty tmp directory resolved at
quake_loyola.config's first import) — every test here that writes through
it must restore FLAGS/BUILD and delete the file afterward so it doesn't
leak state into other tests (e.g. the golden-hash regression suite, which
assumes hardcoded defaults)."""

import platform
import unittest
from unittest import mock

import typer
from typer.testing import CliRunner

from quake_loyola import cli, config, mapgen


class ParseBoolTests(unittest.TestCase):
    def test_accepts_true_like_values(self):
        for value in ("true", "True", "1", "yes", "on", "  ON  "):
            with self.subTest(value=value):
                self.assertTrue(cli._parse_bool(value))

    def test_accepts_false_like_values(self):
        for value in ("false", "False", "0", "no", "off"):
            with self.subTest(value=value):
                self.assertFalse(cli._parse_bool(value))

    def test_rejects_unrecognized_value(self):
        with self.assertRaises(typer.BadParameter):
            cli._parse_bool("maybe")


class ValidateOneTests(unittest.TestCase):
    def test_flag_name_is_case_insensitive_and_parsed_as_bool(self):
        kind, key, value = cli._validate_one("knott_enabled_walkway", "true")
        self.assertEqual((kind, key, value), ("flag", "KNOTT_ENABLED_WALKWAY", True))

    def test_enum_build_setting_accepts_valid_value(self):
        kind, key, value = cli._validate_one("vis_mode", "full")
        self.assertEqual((kind, key, value), ("build", "vis_mode", "full"))

    def test_enum_build_setting_rejects_invalid_value(self):
        with self.assertRaises(typer.BadParameter):
            cli._validate_one("vis_mode", "ultra")

    def test_fog_density_accepts_named_preset(self):
        kind, key, value = cli._validate_one("fog_density", "high")
        self.assertEqual((kind, key, value), ("build", "fog_density", "high"))

    def test_fog_density_accepts_custom_float_string(self):
        _, _, value = cli._validate_one("fog_density", "0.05")
        self.assertEqual(value, "0.05")

    def test_fog_density_rejects_invalid_value(self):
        with self.assertRaises(typer.BadParameter):
            cli._validate_one("fog_density", "extreme")

    def test_boolean_build_setting_parsed_as_bool(self):
        kind, key, value = cli._validate_one("light_extra", "true")
        self.assertEqual((kind, key, value), ("build", "light_extra", True))

    def test_unknown_setting_name_exits_with_code_1(self):
        with self.assertRaises(typer.Exit) as ctx:
            cli._validate_one("not_a_real_setting", "true")
        self.assertEqual(ctx.exception.exit_code, 1)


class CliRunnerConfigCommandTests(unittest.TestCase):
    """CliRunner-based tests for the `ql conf` subcommands, run in-process
    against the shared session-wide config.CONFIG_PATH (see module
    docstring). Every test restores state in tearDown regardless of
    outcome."""

    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        config.reset()

    def test_conf_show_lists_flags_and_build_settings(self):
        result = self.runner.invoke(cli.app, ["conf", "show"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("[flags]", result.stdout)
        self.assertIn("[build]", result.stdout)
        self.assertIn("sky_preset", result.stdout)

    def test_conf_get_known_flag(self):
        result = self.runner.invoke(cli.app, ["conf", "get", "KNOTT_ENABLED"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), str(config.DEFAULTS["KNOTT_ENABLED"]))

    def test_conf_get_known_build_setting(self):
        result = self.runner.invoke(cli.app, ["conf", "get", "vis_mode"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), "fast")

    def test_conf_get_unknown_setting_exits_nonzero(self):
        result = self.runner.invoke(cli.app, ["conf", "get", "nope"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Unknown setting", result.output)

    def test_conf_set_single_pair_round_trips(self):
        result = self.runner.invoke(cli.app, ["conf", "set", "vis_mode", "full"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("vis_mode = full", result.stdout)
        self.assertEqual(config.get_build("vis_mode"), "full")

    def test_conf_set_multiple_name_equals_value_pairs(self):
        result = self.runner.invoke(
            cli.app,
            ["conf", "set", "KNOTT_ENABLED=false", "vis_mode=full"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(config.get("KNOTT_ENABLED"))
        self.assertEqual(config.get_build("vis_mode"), "full")

    def test_conf_set_rejects_arg_missing_equals_in_multi_form(self):
        result = self.runner.invoke(
            cli.app, ["conf", "set", "KNOTT_ENABLED=false", "vis_mode"]
        )
        self.assertNotEqual(result.exit_code, 0)

    def test_conf_path_prints_config_path(self):
        result = self.runner.invoke(cli.app, ["conf", "path"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), str(config.CONFIG_PATH))

    def test_conf_reset_reports_no_file_when_absent(self):
        if config.CONFIG_PATH.exists():
            config.CONFIG_PATH.unlink()
        result = self.runner.invoke(cli.app, ["conf", "reset"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("already using defaults", result.stdout)

    def test_conf_reset_with_yes_flag_skips_confirmation(self):
        config.set_flag("KNOTT_ENABLED", False)
        self.assertTrue(config.CONFIG_PATH.exists())
        result = self.runner.invoke(cli.app, ["conf", "reset", "--yes"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Reset to defaults", result.stdout)
        self.assertFalse(config.CONFIG_PATH.exists())

    def test_conf_reset_declining_confirmation_aborts(self):
        config.set_flag("KNOTT_ENABLED", False)
        self.assertTrue(config.CONFIG_PATH.exists())
        result = self.runner.invoke(cli.app, ["conf", "reset"], input="n\n")
        self.assertNotEqual(result.exit_code, 0)
        # Aborted before deleting — the override survives.
        self.assertTrue(config.CONFIG_PATH.exists())
        self.assertFalse(config.get("KNOTT_ENABLED"))


class CliRunnerGenCommandTests(unittest.TestCase):
    """CliRunner test for `ql gen`'s success path (the RuntimeError-handling
    failure path is already covered by tests/test_cli.py's subprocess-based
    malformed-toml tests, which need a genuinely fresh process/cwd)."""

    def setUp(self):
        self.runner = CliRunner()
        self.map_path = config.REPO_ROOT / "loyola.map"

    def tearDown(self):
        if self.map_path.exists():
            self.map_path.unlink()

    def test_gen_writes_loyola_map(self):
        if self.map_path.exists():
            self.map_path.unlink()
        result = self.runner.invoke(cli.app, ["gen"])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(self.map_path.exists())
        self.assertEqual(self.map_path.read_text(), mapgen.build_map_text())


class CliRunnerBuildCommandTests(unittest.TestCase):
    """`ql build` without ericw-tools installed under REPO_ROOT/.tools/ (true
    here — config.REPO_ROOT resolves to tests/conftest.py's isolated,
    tool-free tmp directory) should generate the map, then fail cleanly on
    the missing-toolchain check, without ever invoking a real subprocess."""

    def setUp(self):
        self.runner = CliRunner()
        self.map_path = config.REPO_ROOT / "loyola.map"

    def tearDown(self):
        if self.map_path.exists():
            self.map_path.unlink()

    def test_build_fails_cleanly_without_ericw_tools(self):
        if self.map_path.exists():
            self.map_path.unlink()
        result = self.runner.invoke(cli.app, ["build"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("ericw-tools not found", result.output)
        # `generate()` (called internally by `build`) should still have run
        # and written loyola.map before the toolchain check failed.
        self.assertTrue(self.map_path.exists())


class EricwToolsVersionSortTests(unittest.TestCase):
    """`_ericw_tools_version` must parse vMAJOR.MINOR.PATCH (and an optional
    -N-gHASH dev-build suffix) out of a `.tools/ericw-tools-*/bin` path so
    the newest install is picked even when installs aren't in lexicographic
    order (e.g. v0.9.0 should sort below v0.18.1, not above it)."""

    def _bin_path(self, dirname: str):
        return config.REPO_ROOT / ".tools" / dirname / "bin"

    def test_parses_plain_release_version(self):
        version = cli._ericw_tools_version(self._bin_path("ericw-tools-v0.18.1-Darwin"))
        self.assertEqual(version, (0, 18, 1, 0))

    def test_parses_dev_build_commit_count(self):
        version = cli._ericw_tools_version(
            self._bin_path("ericw-tools-v0.18.1-32-g6660c5f-Darwin")
        )
        self.assertEqual(version, (0, 18, 1, 32))

    def test_unparseable_name_sorts_lowest(self):
        version = cli._ericw_tools_version(self._bin_path("ericw-tools-mystery"))
        self.assertEqual(version, (0, 0, 0, 0))

    def test_newer_minor_version_outranks_lexicographically_larger_string(self):
        # "v0.9.0" > "v0.18.1" lexicographically, but 0.18.1 is the newer
        # release — max() by _ericw_tools_version must pick v0.18.1.
        candidates = [
            self._bin_path("ericw-tools-v0.9.0-Darwin"),
            self._bin_path("ericw-tools-v0.18.1-Darwin"),
        ]
        newest = max(candidates, key=cli._ericw_tools_version)
        self.assertEqual(newest, self._bin_path("ericw-tools-v0.18.1-Darwin"))


class CliRunnerBuildCommandSuccessTests(unittest.TestCase):
    """`ql build`'s qbsp -> vis -> light -> deploy pipeline, with
    subprocess.run and shutil.copy mocked out so no real toolchain or
    Quake install is required."""

    def setUp(self):
        self.runner = CliRunner()
        self.map_path = config.REPO_ROOT / "loyola.map"
        self.tools_dir = (
            config.REPO_ROOT
            / ".tools"
            / f"ericw-tools-v0.18.1-{platform.system()}"
            / "bin"
        )
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        for tool in ("qbsp", "vis", "light"):
            (self.tools_dir / tool).touch()

    def tearDown(self):
        if self.map_path.exists():
            self.map_path.unlink()
        tools_root = config.REPO_ROOT / ".tools"
        if tools_root.exists():
            import shutil as _shutil

            _shutil.rmtree(tools_root)

    @mock.patch("quake_loyola.cli.Path.mkdir")
    @mock.patch("quake_loyola.cli.shutil.copy")
    @mock.patch("quake_loyola.cli.subprocess.run")
    def test_build_runs_qbsp_vis_light_in_order_and_deploys(
        self, mock_run, mock_copy, _mock_mkdir
    ):
        mock_run.return_value = mock.Mock(returncode=0)
        # `build`'s deploy step copies loyola.bsp/.lit; create stand-ins so
        # shutil.copy (mocked) has something plausible to "copy".
        (config.REPO_ROOT / "loyola.bsp").touch()
        (config.REPO_ROOT / "loyola.lit").touch()
        try:
            result = self.runner.invoke(cli.app, ["build"])
        finally:
            (config.REPO_ROOT / "loyola.bsp").unlink(missing_ok=True)
            (config.REPO_ROOT / "loyola.lit").unlink(missing_ok=True)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(mock_run.call_count, 3)
        qbsp_cmd, vis_cmd, light_cmd = (c.args[0] for c in mock_run.call_args_list)
        self.assertEqual(qbsp_cmd[0], str(self.tools_dir / "qbsp"))
        # qbsp must run with -bsp2, matching justfile's compile/compile-fast
        # recipes — without it, `ql build` compiles to a different BSP
        # format than `just compile`/`just compile-fast` produce.
        self.assertIn("-bsp2", qbsp_cmd)
        self.assertEqual(vis_cmd[0], str(self.tools_dir / "vis"))
        self.assertEqual(light_cmd[0], str(self.tools_dir / "light"))
        self.assertEqual(mock_copy.call_count, 2)
        self.assertIn("Build complete.", result.output)

    @mock.patch("quake_loyola.cli.Path.mkdir")
    @mock.patch("quake_loyola.cli.shutil.copy")
    @mock.patch("quake_loyola.cli.subprocess.run")
    def test_build_passes_vis_fast_and_light_extra_from_build_settings(
        self, mock_run, _mock_copy, _mock_mkdir
    ):
        mock_run.return_value = mock.Mock(returncode=0)
        config.set_build("vis_mode", "fast")
        config.set_build("light_extra", True)
        (config.REPO_ROOT / "loyola.bsp").touch()
        (config.REPO_ROOT / "loyola.lit").touch()
        try:
            result = self.runner.invoke(cli.app, ["build"])
        finally:
            (config.REPO_ROOT / "loyola.bsp").unlink(missing_ok=True)
            (config.REPO_ROOT / "loyola.lit").unlink(missing_ok=True)
            config.reset()

        self.assertEqual(result.exit_code, 0, result.output)
        _, vis_cmd, light_cmd = (c.args[0] for c in mock_run.call_args_list)
        self.assertIn("-fast", vis_cmd)
        self.assertIn("-extra", light_cmd)

    @mock.patch("quake_loyola.cli.Path.mkdir")
    @mock.patch("quake_loyola.cli.shutil.copy")
    @mock.patch("quake_loyola.cli.subprocess.run")
    def test_build_omits_vis_fast_and_light_extra_when_disabled(
        self, mock_run, _mock_copy, _mock_mkdir
    ):
        mock_run.return_value = mock.Mock(returncode=0)
        config.set_build("vis_mode", "full")
        (config.REPO_ROOT / "loyola.bsp").touch()
        (config.REPO_ROOT / "loyola.lit").touch()
        try:
            result = self.runner.invoke(cli.app, ["build"])
        finally:
            (config.REPO_ROOT / "loyola.bsp").unlink(missing_ok=True)
            (config.REPO_ROOT / "loyola.lit").unlink(missing_ok=True)
            config.reset()

        self.assertEqual(result.exit_code, 0, result.output)
        _, vis_cmd, light_cmd = (c.args[0] for c in mock_run.call_args_list)
        self.assertNotIn("-fast", vis_cmd)
        self.assertNotIn("-extra", light_cmd)

    @mock.patch("quake_loyola.cli.shutil.copy")
    @mock.patch("quake_loyola.cli.subprocess.run")
    def test_build_no_deploy_skips_copy(self, mock_run, mock_copy):
        mock_run.return_value = mock.Mock(returncode=0)
        result = self.runner.invoke(cli.app, ["build", "--no-deploy"])
        self.assertEqual(result.exit_code, 0, result.output)
        mock_copy.assert_not_called()

    @mock.patch("quake_loyola.cli.subprocess.run")
    def test_build_reports_subprocess_failure(self, mock_run):
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            1, [str(self.tools_dir / "qbsp")]
        )
        result = self.runner.invoke(cli.app, ["build"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("exited with code", result.output)


if __name__ == "__main__":
    unittest.main()
