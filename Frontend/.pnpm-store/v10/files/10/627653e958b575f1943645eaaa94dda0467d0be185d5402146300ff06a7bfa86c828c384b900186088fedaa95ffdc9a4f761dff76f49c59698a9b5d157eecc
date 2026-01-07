import { createResolver, addComponent, addImportsSources, useNuxt, defineNuxtModule, addTemplate, addPluginTemplate } from '@nuxt/kit';
import * as AllComponents from 'element-plus';
import * as AllIcons from '@element-plus/icons-vue';
import { createUnplugin } from 'unplugin';
import MagicString from 'magic-string';

function resolvePath(path) {
  const { resolvePath: resolvePath2 } = createResolver(import.meta.url);
  return resolvePath2(path);
}
async function resolveComponentPath(path, cache) {
  if (cache) {
    return `#build/${libraryName}-cache.mjs`;
  }
  return await resolvePath(`${libraryName}/${path}`);
}
function getLayersDir(layers) {
  const list = [];
  for (const layer of layers) {
    const srcDir = layer.config.srcDir || layer.cwd;
    if (srcDir.includes("node_modules") && layer.config.elementPlus?.importStyle !== false) {
      list.push(srcDir);
    }
  }
  return list;
}
function isObject(value) {
  return typeof value === "object" && value !== null && !isArray(value);
}
function isFunction(value) {
  return typeof value === "function";
}
function isArray(value) {
  return Array.isArray(value);
}
function isVueComponent(value) {
  return typeof value === "object" && value.name && (value.props || value.emits || value.setup || value.render);
}
function toArray(value) {
  return isArray(value) ? value : [value];
}
function toRegExp(arr, flags) {
  return new RegExp(`\\b(${arr.join("|")})\\b`, flags);
}
async function genLibraryImport([name, as, from], cache) {
  const fromPath = await resolveComponentPath(from, cache);
  return `import { ${name} as ${as} } from '${fromPath}';
`;
}
async function genSideEffectsImport(from) {
  const fromPath = await resolvePath(from);
  return `import '${fromPath}';
`;
}
function genIconPresets(prefix, from) {
  return allIcons.map((name) => {
    return [name, `${prefix}${name}`, from];
  });
}
function camelize(value) {
  return value.replace(/(^|-)(\w)/g, (a, b, c) => c.toUpperCase());
}
function hyphenate(value) {
  return value.replace(/\B([A-Z])/g, "-$1").toLowerCase();
}

const libraryName = "element-plus";
const iconLibraryName = "@element-plus/icons-vue";
const optimizeDeps = ["dayjs", "dayjs/plugin/*.js", "lodash-unified"];
const allComponents = Object.entries(AllComponents).reduce((all, [key, item]) => {
  const regExp = /^El[A-Z]\w+/;
  if (isVueComponent(item) && regExp.test(key) && regExp.test(item.name ?? "")) {
    all.push(key);
  }
  return all;
}, []);
const allIcons = Object.keys(AllIcons);
const allMethods = [
  "ElLoading",
  "ElMessage",
  "ElMessageBox",
  "ElNotification"
];
const allImports = [];
const allBaseImports = [
  ["ID_INJECTION_KEY", "es/hooks/use-id/index.mjs"],
  ["ZINDEX_INJECTION_KEY", "es/hooks/use-z-index/index.mjs"],
  ["provideGlobalConfig", "es/components/config-provider/src/hooks/use-global-config.mjs"]
];
const allNoStylesComponents = [
  "ElAutoResizer",
  "ElCollection",
  "ElCollectionItem",
  "ElTooltipV2"
];
const allDirectives = {
  Loading: ["ElLoadingDirective", "ElLoading"],
  Popover: ["ElPopoverDirective", "ElPopover"],
  InfiniteScroll: "ElInfiniteScroll"
};
const allSubComponents = {
  ElAnchor: ["ElAnchorLink"],
  ElBreadcrumb: ["ElBreadcrumbItem"],
  ElButton: ["ElButtonGroup"],
  ElCarousel: ["ElCarouselItem"],
  ElCheckbox: ["ElCheckboxButton", "ElCheckboxGroup"],
  ElCollapse: ["ElCollapseItem"],
  ElCollection: ["ElCollectionItem"],
  ElContainer: ["ElAside", "ElFooter", "ElHeader", "ElMain"],
  ElDescriptions: ["ElDescriptionsItem"],
  ElDropdown: ["ElDropdownItem", "ElDropdownMenu"],
  ElForm: ["ElFormItem"],
  ElMenu: ["ElMenuItem", "ElMenuItemGroup", "ElSubMenu"],
  ElPopper: ["ElPopperArrow", "ElPopperContent", "ElPopperTrigger"],
  ElRadio: ["ElRadioGroup", "ElRadioButton"],
  ElSkeleton: ["ElSkeletonItem"],
  ElSelect: ["ElOption", "ElOptionGroup"],
  ElSplitter: ["ElSplitterPanel"],
  ElSteps: ["ElStep"],
  ElTable: ["ElTableColumn"],
  ElTableV2: ["ElAutoResizer"],
  ElTabs: ["ElTabPane"],
  ElTimeline: ["ElTimelineItem"],
  ElTour: ["ElTourStep"]
};
const defaultInjectionID = {
  prefix: 1024,
  current: 0
};
const defaultInjectionZIndex = {
  current: 0
};
const defaultInclude = [
  /\.vue$/,
  /\.vue\?vue/,
  /\.vue\?v=/,
  /\.((c|m)?j|t)sx?$/
];
const defaultExclude = [
  /[\\/]node_modules[\\/]/,
  /[\\/]\.git[\\/]/,
  /[\\/]\.nuxt[\\/]/
];
const defaults = {
  components: allComponents,
  subComponents: allSubComponents,
  directives: allDirectives,
  imports: allImports,
  baseImports: allBaseImports,
  importStyle: "css",
  themes: [],
  noStylesComponents: allNoStylesComponents,
  injectionID: defaultInjectionID,
  injectionZIndex: defaultInjectionZIndex,
  include: defaultInclude,
  exclude: defaultExclude,
  namespace: "el",
  defaultLocale: "en",
  appendTo: [],
  installMethods: [],
  icon: "ElIcon"
};

function resolveCache(config) {
  const { defaultLocale } = config;
  const locale = camelize(defaultLocale);
  return {
    filename: `${libraryName}-cache.mjs`,
    getContents: () => {
      return `export * from '${libraryName}';
${defaultLocale !== "en" ? `import ${locale} from '${libraryName}/es/locale/lang/${defaultLocale}.mjs';
export { ${locale} };` : ""}`;
    }
  };
}

function getComponentPath(name) {
  const dir = hyphenate(name.slice(2));
  return `es/components/${dir}/index.mjs`;
}
function resolveComponents(config) {
  const { components, subComponents, icon, cache } = config;
  const icons = icon !== false ? genIconPresets(icon, iconLibraryName) : [];
  const allComponents = /* @__PURE__ */ new Set([...components, ...icons]);
  const subComponentsMap = Object.fromEntries(
    Object.entries(subComponents).reduce((all, [key, values]) => {
      values.forEach((item) => {
        all.push([item, key]);
      });
      return all;
    }, [])
  );
  allComponents.forEach(async (item) => {
    const [name, alias, from] = toArray(item);
    const componentName = subComponentsMap[name] || name;
    const filePath = from !== iconLibraryName ? await resolveComponentPath(getComponentPath(componentName), cache) : await resolvePath(from);
    addComponent({
      export: name,
      name: alias || name,
      filePath
    });
  });
}

function resolveDirectives(config, name) {
  const { directives } = config;
  if (!directives[name]) {
    return void 0;
  }
  const [directive, styleName] = toArray(directives[name]);
  const path = getComponentPath(styleName ?? directive);
  const style = styleName && getStyleDir(config, styleName);
  return [directive, path, style];
}

function resolveGlobalConfig(config) {
  const { globalConfig, cache, defaultLocale } = config;
  const needLocale = !!(cache && defaultLocale !== "en");
  const locale = camelize(defaultLocale);
  let provideConfig = JSON.stringify(globalConfig);
  if (needLocale) {
    provideConfig = JSON.stringify(Object.assign({}, globalConfig, { locale })).replace(`"${locale}"`, locale);
  }
  return {
    filename: `${libraryName}-globalConfig.plugin.mjs`,
    getContents: async () => {
      return `import { defineNuxtPlugin, provideGlobalConfig } from '#imports';
${needLocale ? `import { ${locale} } from '${await resolveComponentPath("", cache)}';
` : ""}
export default defineNuxtPlugin(nuxtApp => { 
  provideGlobalConfig(${provideConfig}, nuxtApp.vueApp, true);
})`;
    }
  };
}

function _resolveImports(imports, cache) {
  imports.forEach(async ([name, path]) => {
    addImportsSources({
      from: await resolveComponentPath(path, cache),
      imports: toArray(name)
    });
  });
}
async function resolveImports(config) {
  const { imports, icon, cache } = config;
  const icons = icon !== false ? genIconPresets(icon) : [];
  const allImports = new Set(imports);
  const allIcons = new Set(icons);
  _resolveImports(allImports, cache);
  addImportsSources({
    from: await resolvePath(iconLibraryName),
    imports: [...allIcons]
  });
}
function resolveBaseImports(config) {
  const { baseImports, cache } = config;
  const methodImports = allMethods.map((name) => {
    return [name, getComponentPath(name)];
  });
  const allBaseImports = /* @__PURE__ */ new Set([...baseImports, ...methodImports]);
  _resolveImports(allBaseImports, cache);
}

function resolveInjection(config) {
  const { injectionID, injectionZIndex } = config;
  return {
    filename: `${libraryName}-injection.plugin.mjs`,
    getContents: () => {
      return `import { defineNuxtPlugin, ID_INJECTION_KEY, ZINDEX_INJECTION_KEY } from '#imports';

export default defineNuxtPlugin(nuxtApp => {
  nuxtApp.vueApp
    .provide(ID_INJECTION_KEY, ${JSON.stringify(injectionID)})
    .provide(ZINDEX_INJECTION_KEY, ${JSON.stringify(injectionZIndex)});
})
`;
    }
  };
}

const localePlugin = createUnplugin((options) => {
  return {
    name: `${libraryName}:locale`,
    enforce: "pre",
    transformInclude(id) {
      const regExp = new RegExp(`${libraryName}/es/hooks/use-locale/index`);
      return !!id.match(regExp);
    },
    transform(code, id) {
      const s = new MagicString(code);
      s.replace("/locale/lang/en", `/locale/lang/${options.locale}`);
      if (s.hasChanged()) {
        return {
          code: s.toString(),
          map: options.sourcemap ? s.generateMap({ source: id, includeContent: true }) : void 0
        };
      }
    }
  };
});

function resolveMethods(config) {
  const { installMethods } = config;
  return {
    filename: `${libraryName}-methods.plugin.mjs`,
    getContents: () => {
      return `import { defineNuxtPlugin, ${installMethods.join(",")} } from '#imports';

export default defineNuxtPlugin(nuxtApp => {
  ${installMethods.reduce((all, name) => `${all}.use(${name})`, "nuxtApp.vueApp")};
})
`;
    }
  };
}

function resolveOptions(config) {
  const { cache, importStyle, namespace, themeChalk } = config;
  const nuxt = useNuxt();
  nuxt.options.build.transpile.push(libraryName);
  nuxt.options.vite.optimizeDeps ||= {};
  nuxt.options.vite.optimizeDeps.include ||= [];
  nuxt.options.vite.optimizeDeps.include.push(...optimizeDeps);
  if (cache) {
    nuxt.options.vite.optimizeDeps.include.push(libraryName);
  } else {
    nuxt.options.vite.optimizeDeps.exclude ||= [];
    nuxt.options.vite.optimizeDeps.exclude.push(libraryName);
  }
  nuxt.options.vite.css ||= {};
  nuxt.options.vite.css.preprocessorOptions ||= {};
  nuxt.options.vite.css.preprocessorOptions.scss ||= {};
  nuxt.options.vite.css.preprocessorOptions.scss.api ??= "modern-compiler";
  nuxt.options.webpack.loaders.scss.api ??= "modern-compiler";
  if (importStyle === "scss" && themeChalk) {
    const files = [];
    const keys = Object.keys(themeChalk);
    const themes = keys.filter((key) => {
      return !key.startsWith("$") && themeChalk[key] && Object.keys(themeChalk[key]).length;
    });
    if (namespace && namespace !== "el") {
      files.push("namespace");
    }
    if (keys.some((key) => key.startsWith("$"))) {
      files.push("common");
    }
    files.push(...themes);
    const additionalData = files.reduce((all, item) => {
      all += `@use "${nuxt.options.buildDir}/${libraryName}-scss-${item}.scss";`;
      return all;
    }, "");
    async function genAdditionalData(old, source, ...arg) {
      const content = isFunction(old) ? await old(source, ...arg) : (old ?? "") + source;
      return additionalData + content;
    }
    if (additionalData) {
      const oldVite = nuxt.options.vite.css.preprocessorOptions.scss.additionalData;
      nuxt.options.vite.css.preprocessorOptions.scss.additionalData = (source, ...arg) => {
        return genAdditionalData(oldVite, source, ...arg);
      };
      const oldWebpack = nuxt.options.webpack.loaders.scss.additionalData;
      nuxt.options.webpack.loaders.scss.additionalData = (source, ...arg) => {
        return genAdditionalData(oldWebpack, source, ...arg);
      };
    }
  }
}

function getStyleDir(config, name) {
  if (config.importStyle === false) {
    return void 0;
  }
  const dir = hyphenate(name.slice(2));
  const type = config.importStyle === "scss" ? "index" : "css";
  return `${libraryName}/es/components/${dir}/style/${type}.mjs`;
}
function resolveStyles(config, name) {
  const { components, noStylesComponents } = config;
  const allComponents = [...components, ...allMethods];
  if (!allComponents.includes(name) || noStylesComponents.includes(name)) {
    return void 0;
  }
  return /^El[A-Z]/.test(name) ? getStyleDir(config, name) : void 0;
}

function resolveTeleports(config) {
  const { namespace, appendTo } = config;
  const defaultId = `#${namespace}-popper-container-`;
  return {
    filename: `${libraryName}-teleports.plugin.mjs`,
    getContents: () => {
      return `import { defineNuxtPlugin } from '#imports'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.hook('app:rendered', (ctx) => {
    if (ctx.ssrContext?.teleports) {
      ctx.ssrContext.teleports = renderTeleports(ctx.ssrContext.teleports)
    }
  })
})

function renderTeleports (teleports) {
  const body = Object.entries(teleports).reduce((all, [key, value]) => {
    if (key.startsWith('${defaultId}') || ${JSON.stringify(appendTo)}.includes(key)) {
      return \`\${all}<div id="\${key.slice(1)}">\${value}</div>\`
    }
    return all
  }, teleports.body || '')
  return { ...teleports, body }
}
`;
    }
  };
}

function resolveThemeChalk(config) {
  const { themeChalk, namespace } = config;
  const files = [];
  const common = {};
  const themes = [];
  if (!themeChalk) {
    return [];
  }
  Object.keys(themeChalk).forEach((key) => {
    if (key.startsWith("$")) {
      const _key = key;
      common[_key] = themeChalk[_key];
    } else {
      themes.push(key);
    }
  });
  if (namespace && namespace !== "el") {
    files.push(genNamespaceFile());
  }
  if (Object.keys(common).length) {
    files.push(genThemeChalkFile("common", common));
  }
  themes.forEach((type) => {
    const config2 = themeChalk[type];
    if (config2 && Object.keys(config2).length) {
      files.push(genThemeChalkFile(type, config2));
    }
  });
  function genNamespaceFile() {
    return {
      filename: `${libraryName}-scss-namespace.scss`,
      write: true,
      getContents: async () => {
        return `@forward '${await resolveComponentPath("theme-chalk/src/mixins/config.scss", false)}' with (
  $namespace: '${namespace}'
);`;
      }
    };
  }
  function genThemeChalkFile(type, config2) {
    return {
      filename: `${libraryName}-scss-${type}.scss`,
      write: true,
      getContents: async () => {
        return `@forward '${await resolveComponentPath(`theme-chalk/src/${type}/var.scss`, false)}' with (
${genScssVariables(config2)}
);`;
      }
    };
  }
  function genScssVariables(config2) {
    function genValue(value) {
      if (isArray(value)) {
        return `(${value.join(", ")})`;
      } else if (isObject(value)) {
        return `(${Object.entries(value).reduce((all, [k, v]) => {
          if (!v) {
            return all;
          }
          all.push(`'${k}': ${genValue(v)}`);
          return all;
        }, []).join(", ")})`;
      } else {
        return value;
      }
    }
    return Object.entries(config2).reduce((all, [key, value]) => {
      if (!value) {
        return all;
      }
      all.push(`  ${key}: ${genValue(value)}`);
      return all;
    }, []).join(",\n");
  }
  return files;
}

function resolveThemes(config) {
  const nuxt = useNuxt();
  const { themes, importStyle } = config;
  const allThemes = new Set(themes);
  if (importStyle === false) {
    return;
  }
  allThemes.forEach(async (item) => {
    const isScss = importStyle === "scss";
    const theme = await resolvePath(`${libraryName}/theme-chalk${isScss ? "/src" : ""}/${item}/css-vars.${isScss ? "scss" : "css"}`);
    nuxt.options.css.push(theme);
  });
}

const componentsRegExp = /(?<=[ (])_?resolveComponent\(\s*["'](lazy-|Lazy)?([^'"]*?)["'][\s,]*[^)]*\)/g;
const directivesRegExp = /(?<=[ (])_?resolveDirective\(\s*["']([^'"]*?)["'][\s,]*[^)]*\)/g;
const methodsRegExp = toRegExp(allMethods, "g");
const transformPlugin = createUnplugin((options) => {
  const { cache, layers, include, exclude, sourcemap, transformStyles, transformDirectives } = options;
  return {
    name: `${libraryName}:transform`,
    enforce: "post",
    transformInclude(id) {
      if (layers.some((layer) => id.startsWith(layer))) {
        return true;
      }
      if (exclude.some((pattern) => id.match(pattern))) {
        return false;
      }
      if (include.some((pattern) => id.match(pattern))) {
        return true;
      }
    },
    async transform(code, id) {
      const styles = /* @__PURE__ */ new Set();
      const directives = [];
      const s = new MagicString(code);
      let no = 0;
      const addStyles = (style) => {
        style && styles.add(style);
      };
      s.replace(componentsRegExp, (full, lazy, name) => {
        addStyles(transformStyles(camelize(name)));
        return full;
      });
      s.replace(methodsRegExp, (full, name) => {
        addStyles(transformStyles(camelize(name)));
        return full;
      });
      s.replace(directivesRegExp, (full, name) => {
        const directiveConfig = transformDirectives(camelize(name));
        if (directiveConfig) {
          const [directive, path, style] = directiveConfig;
          const aliasName = `__el_directive_${no}`;
          no += 1;
          addStyles(style);
          directives.push([directive, aliasName, path]);
          return aliasName;
        }
        return full;
      });
      if (styles.size || directives.length) {
        let imports = "";
        for (const directive of directives) {
          imports += await genLibraryImport(directive, cache);
        }
        for (const style of styles) {
          imports += await genSideEffectsImport(style);
        }
        s.prepend(imports);
      }
      if (s.hasChanged()) {
        return {
          code: s.toString(),
          map: sourcemap ? s.generateMap({ source: id, includeContent: true }) : void 0
        };
      }
    }
  };
});

const module = defineNuxtModule({
  meta: {
    name: libraryName,
    configKey: "elementPlus",
    compatibility: {
      nuxt: ">=3"
    }
  },
  defaults,
  setup(options, nuxt) {
    const layers = getLayersDir(nuxt.options._layers);
    if (!nuxt.options.dev) {
      options.cache = false;
    }
    resolveOptions(options);
    resolveThemes(options);
    resolveBaseImports(options);
    nuxt.options.imports.autoImport !== false && resolveImports(options);
    nuxt.options.components !== false && resolveComponents(options);
    options.cache && addTemplate(resolveCache(options));
    options.globalConfig && addPluginTemplate(resolveGlobalConfig(options));
    options.importStyle === "scss" && options.themeChalk && resolveThemeChalk(options).map(addTemplate);
    if (nuxt.options.ssr !== false) {
      addPluginTemplate(resolveInjection(options));
      addPluginTemplate(resolveTeleports(options));
      options.installMethods.length && addPluginTemplate(resolveMethods(options));
    }
    nuxt.hook("vite:extendConfig", (config, { isClient }) => {
      const mode = isClient ? "client" : "server";
      config.plugins = config.plugins || [];
      config.plugins.push(transformPlugin.vite({
        layers,
        cache: options.cache,
        include: options.include,
        exclude: options.exclude,
        sourcemap: nuxt.options.sourcemap[mode],
        transformStyles: (name) => resolveStyles(options, name),
        transformDirectives: (name) => resolveDirectives(options, name)
      }));
      if (options.defaultLocale !== "en") {
        config.plugins.push(localePlugin.vite({
          sourcemap: nuxt.options.sourcemap[mode],
          locale: options.defaultLocale
        }));
      }
    });
    nuxt.hook("webpack:config", (configs) => {
      configs.forEach((config) => {
        const mode = config.name === "client" ? "client" : "server";
        config.plugins = config.plugins || [];
        config.plugins.push(transformPlugin.webpack({
          layers,
          cache: options.cache,
          include: options.include,
          exclude: options.exclude,
          sourcemap: nuxt.options.sourcemap[mode],
          transformStyles: (name) => resolveStyles(options, name),
          transformDirectives: (name) => resolveDirectives(options, name)
        }));
        if (options.defaultLocale !== "en") {
          config.plugins.push(localePlugin.webpack({
            sourcemap: nuxt.options.sourcemap[mode],
            locale: options.defaultLocale
          }));
        }
      });
    });
  }
});

export { module as default };
