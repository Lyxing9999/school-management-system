export type UseFormService<
  CreateType = never,
  UpdateType = never,
  ReplaceType = never,
  GetType = CreateType
> = {
  create?: (data: CreateType) => Promise<any>;
  update?: UpdateType extends never
    ? undefined
    : (id: string, data: UpdateType) => Promise<any>;
  replace?: ReplaceType extends never
    ? undefined
    : (id: string, data: ReplaceType) => Promise<any>;
  getDetail?: (id: string) => Promise<GetType>;
};
