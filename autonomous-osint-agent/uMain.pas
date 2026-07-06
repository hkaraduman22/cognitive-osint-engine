unit uMain;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, REST.Types, FireDAC.Stan.Intf,
  FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS,
  FireDAC.Phys.Intf, FireDAC.DApt.Intf, Data.DB, FireDAC.Comp.DataSet,
  FireDAC.Comp.Client, REST.Response.Adapter, REST.Client, Data.Bind.Components,
  Data.Bind.ObjectScope, Vcl.Grids, Vcl.DBGrids, Vcl.StdCtrls,
  System.Threading, System.JSON, VCLTee.TeEngine, VCLTee.Series, Vcl.ExtCtrls,
  VCLTee.TeeProcs, VCLTee.Chart;

type
  TfrmMain = class(TForm)
    edtSehir: TEdit;
    cmbSektor: TComboBox;
    cmbCalisanSayisi: TComboBox;
    edtMinPuan: TEdit;
    chkSadeceYatirimAlanlar: TCheckBox;
    btnAra: TButton;
    btnTaramaBaslat: TButton;
    btnAnalizGetir: TButton;
    dbgSonuclar: TDBGrid;
    mmoLoglar: TMemo;
    chtSektor: TChart;

    // API Bilesenleri
    RestClient: TRESTClient;
    RestRequest: TRESTRequest;
    RestResponse: TRESTResponse;
    RestAdapter: TRESTResponseDataSetAdapter;
    MemTableSonuclar: TFDMemTable;
    dsSonuclar: TDataSource;

    // Analitik icin ayri istek bileseni
    RestReqStats: TRESTRequest;
    RestResStats: TRESTResponse;

    procedure btnAraClick(Sender: TObject);
    procedure btnTaramaBaslatClick(Sender: TObject);
    procedure btnAnalizGetirClick(Sender: TObject);
    procedure dbgSonuclarDblClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
  private
    procedure GelismisAramaYap;
    procedure LogYaz(AMesaj: string);
  public
  end;

var
  frmMain: TfrmMain;

implementation

{$R *.dfm}

procedure TfrmMain.LogYaz(AMesaj: string);
begin
  mmoLoglar.Lines.Add(FormatDateTime('hh:nn:ss', Now) + ' [SYS] > ' + AMesaj);
end;

procedure TfrmMain.FormCreate(Sender: TObject);
begin
  if cmbSektor.Items.Count = 0 then
  begin
    cmbSektor.Items.Add('Tümü');
    cmbSektor.Items.Add('Yazılım');
    cmbSektor.Items.Add('Otomotiv');
    cmbSektor.Items.Add('Tekstil');
  end;
  cmbSektor.ItemIndex := 0;

  if cmbCalisanSayisi.Items.Count = 0 then
  begin
    cmbCalisanSayisi.Items.Add('Tümü');
    cmbCalisanSayisi.Items.Add('1-50');
    cmbCalisanSayisi.Items.Add('50-250');
    cmbCalisanSayisi.Items.Add('250+');
  end;
  cmbCalisanSayisi.ItemIndex := 0;

  LogYaz('Sistem baslatildi. Tum moduller (Code Freeze) yayinda.');
end;

// 5. GUN: VİTRİN VE FİLTRELEME
procedure TfrmMain.GelismisAramaYap;
begin
  LogYaz('Filtrelere gore veritabaninda arama yapiliyor...');
  RestRequest.Params.Clear;
  RestRequest.Method := rmGET;
  RestRequest.Resource := 'companies';

  if Trim(edtSehir.Text) <> '' then RestRequest.AddParameter('sehir', Trim(edtSehir.Text), pkGETrsUnsaved);
  if (cmbSektor.ItemIndex > 0) then RestRequest.AddParameter('sektor', cmbSektor.Text, pkGETrsUnsaved);
  if (cmbCalisanSayisi.ItemIndex > 0) then RestRequest.AddParameter('calisan_araligi', cmbCalisanSayisi.Text, pkGETrsUnsaved);
  if Trim(edtMinPuan.Text) <> '' then RestRequest.AddParameter('min_puan', Trim(edtMinPuan.Text), pkGETrsUnsaved);
  if chkSadeceYatirimAlanlar.Checked then RestRequest.AddParameter('yatirim_aldi_mi', 'true', pkGETrsUnsaved);

  try
    RestRequest.Execute;
    if RestResponse.StatusCode = 200 then
    begin
      MemTableSonuclar.Close;
      MemTableSonuclar.Open;
      LogYaz('Basarili: ' + IntToStr(MemTableSonuclar.RecordCount) + ' kayit bulundu.');
    end
    else
      LogYaz('Hata: API Kodu ' + RestResponse.StatusCode.ToString);
  except
    on E: Exception do LogYaz('Baglanti Hatasi: ' + E.Message);
  end;
end;

procedure TfrmMain.btnAraClick(Sender: TObject);
begin
  GelismisAramaYap;
end;

// 4. GUN: OSINT BOTUNU ASENKRON TETIKLEME
procedure TfrmMain.btnTaramaBaslatClick(Sender: TObject);
begin
  LogYaz('OSINT Taramasi baslatiliyor. Bot ve LLM isleme alindi...');
  btnTaramaBaslat.Enabled := False;

  TTask.Run(procedure
  begin
    RestReqStats.Method := rmPOST;
    RestReqStats.Resource := 'companies/scan';

    try
      RestReqStats.Execute;
      TThread.Queue(nil, procedure
      begin
        if RestResStats.StatusCode = 200 then
          LogYaz('MUKEMMEL: Bot verileri cekti, LLM eledi ve DB''ye kaydedildi!')
        else
          LogYaz('Hata: Tarama sirasinda sorun olustu. Kod: ' + RestResStats.StatusCode.ToString);

        btnTaramaBaslat.Enabled := True;
      end);
    except
      on E: Exception do
      begin
        TThread.Queue(nil, procedure
        begin
          LogYaz('Baglanti Hatasi (Bot Cagrilarinda): ' + E.Message);
          btnTaramaBaslat.Enabled := True;
        end);
      end;
    end;
  end);
end;

// 6. GUN: ANALITIK VE GRAFIKLER (TChart)
procedure TfrmMain.btnAnalizGetirClick(Sender: TObject);
var
  JSONObj: TJSONObject;
  JSONPair: TJSONPair;
  PieSeries: TPieSeries;
  i: Integer;
begin
  LogYaz('Analitik endpoint''inden sektorel dagilim verisi cekiliyor...');
  RestReqStats.Method := rmGET;
  RestReqStats.Resource := 'stats/industry-distribution';

  try
    RestReqStats.Execute;
    if RestResStats.StatusCode = 200 then
    begin
      // Eski grafigi temizle
      chtSektor.RemoveAllSeries;
      PieSeries := TPieSeries.Create(chtSektor);
      chtSektor.AddSeries(PieSeries);

      // JSON Pars Etme
      JSONObj := TJSONObject.ParseJSONValue(RestResStats.Content) as TJSONObject;
      if Assigned(JSONObj) then
      begin
        try
          for i := 0 to JSONObj.Count - 1 do
          begin
            JSONPair := JSONObj.Pairs[i];
            PieSeries.AddPie(StrToIntDef(JSONPair.JsonValue.Value, 0), JSONPair.JsonString.Value, clTeeColor);
          end;
          LogYaz('Grafik basariyla cizildi.');
        finally
          JSONObj.Free;
        end;
      end;
    end
    else
      LogYaz('Analitik verisi alinamadi.');
  except
    on E: Exception do LogYaz('Analitik Hatasi: ' + E.Message);
  end;
end;

// 5. GUN: DETAY EKRANI
procedure TfrmMain.dbgSonuclarDblClick(Sender: TObject);
var
  Detay: string;
begin
  if MemTableSonuclar.IsEmpty then Exit;

  // JSON'dan gelen field isimlerine gore (Swagger'a uygun varsayilmistir)
  Detay := 'Firma: ' + MemTableSonuclar.FieldByName('firma_adi').AsString + #13#10 +
           'Sektor: ' + MemTableSonuclar.FieldByName('sektor').AsString + #13#10 +
           'Guven Puani: ' + MemTableSonuclar.FieldByName('guven_puani').AsString;

  ShowMessage(Detay);
  LogYaz(MemTableSonuclar.FieldByName('firma_adi').AsString + ' detaylari incelendi.');
end;

end.